#!/usr/bin/env python3
"""Genera borradores de correo a partir de plantillas versionadas."""

from __future__ import annotations

import argparse
import re
import string
import tomllib
from pathlib import Path

import cronograma
import estado


RAIZ = Path(__file__).resolve().parents[1]
BUILD_CORREOS = RAIZ / "build" / "correos"
PLANTILLAS = RAIZ / "correos" / "plantillas"
ARCHIVO_CURSO = RAIZ / "config" / "curso.tex"
TIPOS = ("bienvenida", "aviso-posclase")


def leer_dato_curso(nombre: str) -> str:
    """Lee un comando simple definido en config/curso.tex."""

    contenido = ARCHIVO_CURSO.read_text(encoding="utf-8")
    coincidencia = re.search(
        rf"\\newcommand\s*\{{\s*\\{re.escape(nombre)}\s*\}}\s*"
        rf"\{{\s*([^{{}}]+?)\s*\}}",
        contenido,
        flags=re.DOTALL,
    )
    if coincidencia is None:
        raise ValueError(
            f"No se encontró \\{nombre} en config/curso.tex."
        )
    return " ".join(coincidencia.group(1).split())


def cargar_toml(ruta: Path) -> dict:
    """Carga un TOML y produce un error legible si no existe."""

    if not ruta.is_file():
        raise FileNotFoundError(f"No existe {ruta}.")
    with ruta.open("rb") as archivo:
        return tomllib.load(archivo)


def escribir_atomico(ruta: Path, contenido: str) -> None:
    """Escribe un borrador completo sin dejar archivos parciales."""

    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(
        contenido.rstrip() + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporal.replace(ruta)


def lista(elementos: list[str]) -> str:
    """Convierte una lista TOML en viñetas de texto plano."""

    return "\n".join(f"- {elemento.strip()}" for elemento in elementos)


def bloque(titulo: str, contenido: str | list[str]) -> str:
    """Construye un bloque opcional con título."""

    if isinstance(contenido, list):
        cuerpo = lista(contenido)
    else:
        cuerpo = contenido.strip()
    if not cuerpo:
        return ""
    return f"{titulo}:\n{cuerpo}\n"


def plantilla(nombre: str) -> string.Template:
    """Carga una plantilla de correo versionada."""

    ruta = PLANTILLAS / f"{nombre}.txt"
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe la plantilla {ruta}.")
    return string.Template(ruta.read_text(encoding="utf-8"))


def asunto(texto: str, nombre_curso: str) -> str:
    """Sustituye el marcador legible {curso} dentro del asunto."""

    return texto.strip().replace("{curso}", nombre_curso)


def crear_bienvenida(edicion: str) -> str:
    """Genera el correo inicial de una edición."""

    ruta = (
        RAIZ / "ediciones" / edicion
        / "operacion" / "bienvenida.toml"
    )
    datos = cargar_toml(ruta)
    bienvenida = datos.get("bienvenida", {})
    comunicacion = datos.get("comunicacion", {})
    nombre_curso = leer_dato_curso("nombreCurso")
    docente = leer_dato_curso("docenteCurso")

    introduccion = bienvenida.get("introduccion", "").strip()
    if not introduccion:
        raise ValueError(
            "bienvenida.toml necesita [bienvenida].introduccion."
        )

    valores = {
        "asunto": asunto(
            bienvenida.get(
                "asunto",
                "{curso} — bienvenida e información inicial",
            ),
            nombre_curso,
        ),
        "saludo": bienvenida.get(
            "saludo",
            "Apreciadas y apreciados estudiantes:",
        ).strip(),
        "introduccion": introduccion,
        "bloque_documentos": bloque(
            "Documentos e información inicial",
            bienvenida.get("documentos", []),
        ),
        "bloque_carpeta": bloque(
            "Carpeta compartida del curso",
            comunicacion.get("enlace_carpeta", ""),
        ),
        "bloque_preparacion": bloque(
            "Preparación inicial",
            bienvenida.get("preparacion", []),
        ),
        "bloque_avisos": bloque(
            "Otros avisos",
            bienvenida.get("avisos", []),
        ),
        "docente": docente,
    }
    return plantilla("bienvenida").substitute(valores)


def crear_aviso_posclase(edicion: str) -> str:
    """Genera el aviso operativo posterior a una sesión."""

    sesiones = cronograma.obtener_sesiones(edicion)
    datos = estado.cargar_estado(edicion)
    _, siguiente = estado.localizar_sesiones(datos, sesiones)
    avance = datos["avance"]
    proxima = datos["proxima_sesion"]
    comunicacion = datos.get("comunicacion", {})
    nombre_curso = leer_dato_curso("nombreCurso")
    docente = leer_dato_curso("docenteCurso")

    if siguiente is None:
        referencia_proxima = (
            "No hay otra sesión registrada en el calendario."
        )
    else:
        referencia_proxima = (
            "La próxima sesión corresponde a la semana "
            f"{siguiente['semana']}, sesión {siguiente['sesion']}, "
            f"el {estado.fecha_larga(siguiente['fecha'])}."
        )

    valores = {
        "asunto": asunto(
            comunicacion.get(
                "asunto",
                "{curso} — aviso posterior a clase",
            ),
            nombre_curso,
        ),
        "saludo": comunicacion.get(
            "saludo",
            "Apreciadas y apreciados estudiantes:",
        ).strip(),
        "situacion": avance.get("situacion", "").strip(),
        "referencia_proxima": referencia_proxima,
        "enfoque": proxima.get("enfoque", "").strip(),
        "bloque_carpeta": bloque(
            "Carpeta compartida del curso",
            comunicacion.get("enlace_carpeta", ""),
        ),
        "bloque_preparacion": bloque(
            "Preparación para la próxima sesión",
            proxima.get("preparacion", []),
        ),
        "bloque_avisos": bloque(
            "Otros avisos",
            proxima.get("avisos", []),
        ),
        "docente": docente,
    }
    return plantilla("aviso-posclase").substitute(valores)


def generar(seleccion: set[str] | None = None) -> list[Path]:
    """Genera todos los correos o únicamente los seleccionados."""

    edicion = cronograma.leer_edicion_activa()
    elegidos = seleccion or set(TIPOS)
    desconocidos = elegidos - set(TIPOS)
    if desconocidos:
        raise ValueError(
            "Tipos de correo desconocidos: "
            + ", ".join(sorted(desconocidos))
        )

    generadores = {
        "bienvenida": crear_bienvenida,
        "aviso-posclase": crear_aviso_posclase,
    }
    salidas: list[Path] = []

    for nombre in TIPOS:
        if nombre not in elegidos:
            continue
        destino = BUILD_CORREOS / f"{nombre}.txt"
        escribir_atomico(destino, generadores[nombre](edicion))
        salidas.append(destino)

    return salidas


def argumentos() -> argparse.Namespace:
    """Lee las opciones de ejecución independiente."""

    parser = argparse.ArgumentParser(
        description="Genera borradores de correo del curso."
    )
    parser.add_argument(
        "--only",
        action="append",
        choices=TIPOS,
        help="Genera solamente el tipo indicado.",
    )
    return parser.parse_args()


def main() -> None:
    """Genera y anuncia las salidas."""

    opciones = argumentos()
    seleccion = set(opciones.only) if opciones.only else None
    for ruta in generar(seleccion):
        print(f"Generado: {ruta.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
