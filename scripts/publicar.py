
#!/usr/bin/env python3

"""Publica en Google Drive los archivos de la edición activa."""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


# scripts/ está dentro de la raíz del repositorio.
RAIZ_REPO = Path(__file__).resolve().parent.parent

# Este archivo constituye la única fuente de verdad
# para determinar el semestre activo.
ARCHIVO_EDICION_ACTIVA = (
    RAIZ_REPO / "config" / "edicion-activa.tex"
)


def cargar_argumentos():
    """Procesa las opciones escritas en la terminal."""

    parser = argparse.ArgumentParser(
        description=(
            "Publica en Drive los archivos "
            "de la edición activa."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Ejecuta realmente la publicación. "
            "Sin esta opción solo se simula."
        ),
    )

    parser.add_argument(
        "--only",
        action="append",
        metavar="NOMBRE",
        help=(
            "Publica solamente la categoría indicada. "
            "Puede utilizarse más de una vez."
        ),
    )

    return parser.parse_args()


def detectar_edicion_activa():
    """Extrae \\edicionActiva del archivo LaTeX."""

    if not ARCHIVO_EDICION_ACTIVA.is_file():
        sys.exit(
            "ERROR: no existe config/edicion-activa.tex."
        )

    contenido = ARCHIVO_EDICION_ACTIVA.read_text(
        encoding="utf-8"
    )

    coincidencia = re.search(
        r"\\newcommand\s*"
        r"\{\s*\\edicionActiva\s*\}\s*"
        r"\{\s*([^{}]+?)\s*\}",
        contenido,
    )

    if coincidencia is None:
        sys.exit(
            "ERROR: no se pudo determinar la edición activa."
        )

    edicion = coincidencia.group(1).strip()

    # Impide interpretar accidentalmente una ruta arbitraria.
    if re.fullmatch(r"\d{4}-[12]", edicion) is None:
        sys.exit(
            f"ERROR: formato de edición no válido: {edicion}"
        )

    return edicion


def cargar_configuracion(edicion):
    """Lee publicacion.json de la edición activa."""

    ruta = (
        RAIZ_REPO
        / "ediciones"
        / edicion
        / "publicacion.json"
    )

    if not ruta.is_file():
        sys.exit(
            f"ERROR: no existe "
            f"{ruta.relative_to(RAIZ_REPO)}."
        )

    try:
        with ruta.open(encoding="utf-8") as archivo:
            configuracion = json.load(archivo)

    except json.JSONDecodeError as error:
        sys.exit(
            f"ERROR: publicacion.json no es válido: {error}"
        )

    if "remoto" not in configuracion:
        sys.exit(
            "ERROR: publicacion.json no define 'remoto'."
        )

    if "publicaciones" not in configuracion:
        sys.exit(
            "ERROR: publicacion.json no define "
            "'publicaciones'."
        )

    if not configuracion["publicaciones"]:
        sys.exit(
            "ERROR: no hay publicaciones configuradas."
        )

    return configuracion


def seleccionar_publicaciones(publicaciones, seleccion):
    """Selecciona todas las categorías o solo las solicitadas."""

    nombres = [
        publicacion["nombre"]
        for publicacion in publicaciones
    ]

    # Los nombres deben ser únicos.
    if len(nombres) != len(set(nombres)):
        sys.exit(
            "ERROR: hay nombres de publicación duplicados."
        )

    if not seleccion:
        return publicaciones

    desconocidas = set(seleccion) - set(nombres)

    if desconocidas:
        sys.exit(
            "ERROR: categorías desconocidas: "
            + ", ".join(sorted(desconocidas))
        )

    return [
        publicacion
        for publicacion in publicaciones
        if publicacion["nombre"] in seleccion
    ]


def validar_publicacion(publicacion):
    """Comprueba los campos y archivos de una categoría."""

    campos = {
        "nombre",
        "origen",
        "destino",
        "archivos",
    }

    faltantes = campos - set(publicacion)

    if faltantes:
        sys.exit(
            "ERROR: faltan campos en una publicación: "
            + ", ".join(sorted(faltantes))
        )

    origen = (
        RAIZ_REPO / publicacion["origen"]
    ).resolve()

    if not origen.is_dir():
        sys.exit(
            f"ERROR: no existe el origen de "
            f"'{publicacion['nombre']}': {origen}"
        )

    archivos_faltantes = [
        nombre
        for nombre in publicacion["archivos"]
        if not (origen / nombre).is_file()
    ]

    if archivos_faltantes:
        sys.exit(
            f"ERROR: faltan archivos para "
            f"'{publicacion['nombre']}': "
            + ", ".join(archivos_faltantes)
        )

    return origen


def ejecutar_publicacion(
    remoto,
    publicacion,
    origen,
    aplicar,
):
    """Ejecuta una categoría de publicación mediante rclone."""

    destino_remoto = (
        f"{remoto}:{publicacion['destino']}"
    )

    comando = [
        "rclone",
        "copy",
        str(origen),
        destino_remoto,
        "--files-from",
        "-",
        "--verbose",
    ]

    if not aplicar:
        comando.append("--dry-run")

    print()
    print("=" * 60)
    print(f"Categoría: {publicacion['nombre']}")
    print(f"Origen:    {origen}")
    print(f"Destino:   {destino_remoto}")
    print("Archivos:")

    for nombre in publicacion["archivos"]:
        print(f"  - {nombre}")

    # La lista explícita evita subir archivos no autorizados.
    lista_archivos = (
        "\n".join(publicacion["archivos"]) + "\n"
    )

    resultado = subprocess.run(
        comando,
        input=lista_archivos,
        text=True,
        check=False,
    )

    if resultado.returncode != 0:
        sys.exit(
            f"ERROR: falló la categoría "
            f"'{publicacion['nombre']}' "
            f"con código {resultado.returncode}."
        )


def main():
    """Coordina la detección, validación y publicación."""

    argumentos = cargar_argumentos()

    if shutil.which("rclone") is None:
        sys.exit(
            "ERROR: rclone no está disponible."
        )

    edicion = detectar_edicion_activa()
    configuracion = cargar_configuracion(edicion)

    publicaciones = seleccionar_publicaciones(
        configuracion["publicaciones"],
        argumentos.only,
    )

    if argumentos.apply:
        print(
            "MODO PUBLICACIÓN: Google Drive será actualizado."
        )
    else:
        print(
            "MODO SIMULACIÓN: Google Drive no será modificado."
        )

    print(f"Edición activa: {edicion}")

    for publicacion in publicaciones:
        origen = validar_publicacion(publicacion)

        ejecutar_publicacion(
            configuracion["remoto"],
            publicacion,
            origen,
            argumentos.apply,
        )

    print()
    if argumentos.apply:
        print("Publicación terminada correctamente.")
    else:
        print(
            "Simulación terminada. "
            "Usa --apply para publicar."
        )


if __name__ == "__main__":
    main()