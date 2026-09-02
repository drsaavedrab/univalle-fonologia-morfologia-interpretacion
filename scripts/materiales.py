#!/usr/bin/env python3

"""Convierte materiales DOCX declarados para publicación en PDF."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath


RAIZ_REPO = Path(__file__).resolve().parent.parent
ARCHIVO_EDICION_ACTIVA = RAIZ_REPO / "config" / "edicion-activa.tex"
SCRIPT_WORD = RAIZ_REPO / "scripts" / "exportar-docx-word.ps1"


class ErrorMaterial(RuntimeError):
    """Representa un error controlado durante la preparación."""


def detectar_edicion_activa():
    """Lee la edición activa definida en LaTeX."""

    if not ARCHIVO_EDICION_ACTIVA.is_file():
        raise ErrorMaterial("no existe config/edicion-activa.tex")

    contenido = ARCHIVO_EDICION_ACTIVA.read_text(encoding="utf-8")
    coincidencia = re.search(
        r"\\newcommand\s*\{\s*\\edicionActiva\s*\}\s*"
        r"\{\s*([^{}]+?)\s*\}",
        contenido,
    )
    if coincidencia is None:
        raise ErrorMaterial("no se pudo determinar la edición activa")

    edicion = coincidencia.group(1).strip()
    if re.fullmatch(r"\d{4}-[12]", edicion) is None:
        raise ErrorMaterial(f"formato de edición no válido: {edicion}")
    return edicion


def cargar_publicaciones(edicion):
    """Carga las publicaciones de la edición indicada."""

    ruta = RAIZ_REPO / "ediciones" / edicion / "publicacion.json"
    if not ruta.is_file():
        raise ErrorMaterial(f"no existe {ruta.relative_to(RAIZ_REPO)}")
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ErrorMaterial(f"publicacion.json no es válido: {error}") from error
    return datos.get("publicaciones", [])


def seleccionar_publicaciones(publicaciones, seleccion):
    """Limita la preparación a las categorías solicitadas."""

    if not seleccion:
        return publicaciones
    nombres = {item.get("nombre") for item in publicaciones}
    desconocidas = set(seleccion) - nombres
    if desconocidas:
        raise ErrorMaterial(
            "categorías desconocidas: " + ", ".join(sorted(desconocidas))
        )
    return [item for item in publicaciones if item.get("nombre") in seleccion]


def ruta_relativa(valor, campo):
    """Valida una ruta relativa escrita con separadores POSIX."""

    if not isinstance(valor, str) or not valor.strip():
        raise ErrorMaterial(f"'{campo}' debe ser una ruta no vacía")
    ruta = PurePosixPath(valor.replace("\\", "/"))
    if ruta.is_absolute() or any(parte in {"", ".", ".."} for parte in ruta.parts):
        raise ErrorMaterial(f"ruta no válida en '{campo}': {valor}")
    return ruta


def resolver_dentro_raiz(ruta, base, campo):
    """Resuelve una ruta y comprueba que permanezca dentro de su base."""

    destino = (base / Path(*ruta.parts)).resolve()
    try:
        destino.relative_to(base.resolve())
    except ValueError as error:
        raise ErrorMaterial(f"'{campo}' escapa de su carpeta autorizada") from error
    return destino


def encontrar_soffice():
    """Localiza LibreOffice en rutas habituales."""

    nombres = ["soffice", "libreoffice"]
    candidatos = [shutil.which(nombre) for nombre in nombres]
    candidatos.extend(
        [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        ]
    )
    for candidato in candidatos:
        if candidato and Path(candidato).is_file():
            return str(Path(candidato))
    return None


def convertir_word(fuente, salida_temporal):
    """Exporta mediante Microsoft Word en Windows."""

    if os.name != "nt":
        raise ErrorMaterial("Microsoft Word solo está disponible en Windows")
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell is None or not SCRIPT_WORD.is_file():
        raise ErrorMaterial("no está disponible el exportador de Microsoft Word")

    resultado = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT_WORD),
            str(fuente),
            str(salida_temporal),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode != 0 or not salida_temporal.is_file():
        detalle = (resultado.stderr or resultado.stdout).strip()
        raise ErrorMaterial(f"Microsoft Word no pudo exportar el DOCX: {detalle}")


def convertir_libreoffice(fuente, salida_temporal):
    """Exporta mediante LibreOffice en cualquier sistema compatible."""

    soffice = encontrar_soffice()
    if soffice is None:
        raise ErrorMaterial("LibreOffice no está instalado o no se encontró soffice")

    with tempfile.TemporaryDirectory(prefix="material-docx-") as temporal:
        carpeta = Path(temporal)
        resultado = subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(carpeta),
                str(fuente),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        generado = carpeta / f"{fuente.stem}.pdf"
        if resultado.returncode != 0 or not generado.is_file():
            detalle = (resultado.stderr or resultado.stdout).strip()
            raise ErrorMaterial(f"LibreOffice no pudo exportar el DOCX: {detalle}")
        shutil.copy2(generado, salida_temporal)


def convertir_docx(fuente, destino, motor):
    """Convierte una fuente DOCX de forma atómica."""

    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="material-pdf-") as temporal:
        salida_temporal = Path(temporal) / destino.name
        errores = []

        motores = [motor]
        if motor == "auto":
            motores = ["word", "libreoffice"] if os.name == "nt" else ["libreoffice"]

        for candidato in motores:
            try:
                if candidato == "word":
                    convertir_word(fuente, salida_temporal)
                elif candidato == "libreoffice":
                    convertir_libreoffice(fuente, salida_temporal)
                else:
                    raise ErrorMaterial(f"motor desconocido: {candidato}")
                os.replace(salida_temporal, destino)
                return candidato
            except ErrorMaterial as error:
                errores.append(f"{candidato}: {error}")

        raise ErrorMaterial("; ".join(errores))


def preparar_publicaciones(publicaciones, forzar=False, motor="auto"):
    """Genera los PDF declarados en las categorías seleccionadas."""

    resultados = []
    for publicacion in publicaciones:
        conversiones = publicacion.get("conversiones", [])
        if not conversiones:
            continue
        if not isinstance(conversiones, list):
            raise ErrorMaterial("'conversiones' debe ser una lista")

        origen_rel = ruta_relativa(publicacion.get("origen"), "origen")
        origen = resolver_dentro_raiz(origen_rel, RAIZ_REPO, "origen")
        archivos = set(publicacion.get("archivos", []))

        for conversion in conversiones:
            if not isinstance(conversion, dict):
                raise ErrorMaterial("cada conversión debe ser una tabla JSON")
            fuente_rel = ruta_relativa(conversion.get("fuente"), "fuente")
            salida_rel = ruta_relativa(conversion.get("salida"), "salida")
            fuente = resolver_dentro_raiz(fuente_rel, RAIZ_REPO, "fuente")
            destino = resolver_dentro_raiz(salida_rel, origen, "salida")

            if fuente.suffix.lower() != ".docx":
                raise ErrorMaterial(f"la fuente no es DOCX: {fuente_rel}")
            if destino.suffix.lower() != ".pdf":
                raise ErrorMaterial(f"la salida no es PDF: {salida_rel}")
            if not fuente.is_file():
                raise ErrorMaterial(f"no existe la fuente: {fuente_rel}")
            if salida_rel.as_posix() not in archivos:
                raise ErrorMaterial(
                    f"la salida '{salida_rel}' no figura en 'archivos' de "
                    f"'{publicacion.get('nombre', 'sin nombre')}'"
                )

            actualizado = (
                destino.is_file()
                and destino.stat().st_mtime >= fuente.stat().st_mtime
            )
            if actualizado and not forzar:
                resultados.append(("vigente", fuente_rel, salida_rel, None))
                continue

            usado = convertir_docx(fuente, destino, motor)
            resultados.append(("generado", fuente_rel, salida_rel, usado))

    return resultados


def mostrar_resultados(resultados):
    """Imprime un resumen legible de la preparación."""

    if not resultados:
        print("No hay materiales DOCX configurados para preparar.")
        return
    for estado, fuente, salida, motor in resultados:
        detalle = f" mediante {motor}" if motor else ""
        print(f"{estado.capitalize()}: {fuente} -> {salida}{detalle}")


def cargar_argumentos():
    """Define la interfaz de línea de comandos."""

    parser = argparse.ArgumentParser(
        description="Convierte a PDF los materiales DOCX de la edición activa."
    )
    parser.add_argument("--only", action="append", metavar="CATEGORIA")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--engine",
        choices=["auto", "word", "libreoffice"],
        default="auto",
    )
    return parser.parse_args()


def main():
    """Prepara materiales sin publicar en Drive."""

    argumentos = cargar_argumentos()
    try:
        edicion = detectar_edicion_activa()
        publicaciones = cargar_publicaciones(edicion)
        seleccionadas = seleccionar_publicaciones(publicaciones, argumentos.only)
        resultados = preparar_publicaciones(
            seleccionadas,
            forzar=argumentos.force,
            motor=argumentos.engine,
        )
        print(f"Edición activa: {edicion}")
        mostrar_resultados(resultados)
    except ErrorMaterial as error:
        sys.exit(f"ERROR: {error}")


if __name__ == "__main__":
    main()