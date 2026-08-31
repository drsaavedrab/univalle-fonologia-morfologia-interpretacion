"""
Genera el estado público del curso.

Fuente editable:

- ediciones/<periodo>/operacion/estado.toml

Salidas automáticas:

- build/estado-contenido.tex
"""

from __future__ import annotations

import tomllib
from datetime import date, datetime
from pathlib import Path

import cronograma


RAIZ = Path(__file__).resolve().parents[1]
BUILD = RAIZ / "build"

DIAS = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)

# Abreviaturas institucionales utilizadas en la ficha de estado.
DIAS_ABREVIADOS = (
    "lu.",
    "ma.",
    "mc.",
    "ju.",
    "vn.",
    "sa.",
    "do.",
)

MESES = (
    "",
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


def fecha_larga(valor: date) -> str:
    """Convierte una fecha en «miércoles 2 de septiembre de 2026»."""

    return (
        f"{DIAS[valor.weekday()]} {valor.day} "
        f"de {MESES[valor.month]} de {valor.year}"
    )


def fecha_estado(valor: date) -> str:
    """Convierte una fecha en «MC. 2 de septiembre de 2026»."""

    return (
        f"{DIAS_ABREVIADOS[valor.weekday()]} / {valor.day} "
        f"de {MESES[valor.month]} de {valor.year}"
    )


def escapar_latex(texto: str) -> str:
    """Escapa caracteres especiales en texto operativo plano."""

    reemplazos = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }

    return "".join(
        reemplazos.get(caracter, caracter)
        for caracter in texto
    )


def lista_latex(elementos: list[str]) -> list[str]:
    """Convierte una lista de textos en un entorno itemize."""

    if not elementos:
        return [r"\emph{Sin elementos registrados.}"]

    lineas = [r"\begin{itemize}"]
    lineas.extend(
        rf"    \item {escapar_latex(elemento)}"
        for elemento in elementos
    )
    lineas.append(r"\end{itemize}")
    return lineas


def cargar_estado(edicion: str) -> dict:
    """Lee y valida la estructura mínima de estado.toml."""

    ruta = (
        RAIZ
        / "ediciones"
        / edicion
        / "operacion"
        / "estado.toml"
    )

    with ruta.open("rb") as archivo:
        estado = tomllib.load(archivo)


    if "avance" not in estado or "proxima_sesion" not in estado:
        raise ValueError(
            "estado.toml necesita [avance] y [proxima_sesion]."
        )

    return estado


def localizar_sesiones(
    estado: dict,
    sesiones: list[dict],
) -> tuple[dict, dict | None]:
    """Localiza la sesión de referencia y la siguiente sesión."""

    avance = estado["avance"]
    clave = (avance.get("semana"), avance.get("sesion"))

    for posicion, sesion in enumerate(sesiones):
        if (sesion["semana"], sesion["sesion"]) == clave:
            siguiente = (
                sesiones[posicion + 1]
                if posicion + 1 < len(sesiones)
                else None
            )
            return sesion, siguiente

    raise ValueError(
        "La sesión indicada en [avance] no existe en el calendario: "
        f"{clave[0]}-{clave[1]}."
    )


def crear_latex(
    estado: dict,
    referencia: dict,
    siguiente: dict | None,
    generado: datetime,
) -> str:
    """Construye las dos páginas públicas del estado del curso."""

    avance = estado["avance"]
    proxima = estado["proxima_sesion"]
    situacion = avance.get("situacion", "").strip()

    if not situacion:
        raise ValueError(
            "[avance].situacion debe describir el estado presente."
        )

    hora = generado.strftime("%I.%M.%S")
    periodo = "a. m." if generado.hour < 12 else "p. m."

    if siguiente is None:
        proxima_semana = "—"
        proxima_numero = "—"
        proxima_fecha = "Sin fecha registrada"
    else:
        proxima_semana = str(siguiente["semana"])
        proxima_numero = siguiente["sesion"]
        proxima_fecha = fecha_estado(siguiente["fecha"])

    lineas = [
        r"\begin{fichaestado}",
        r"\begin{center}",
        r"{\small\textsc{Generado}}\\[2pt]",
        (
            rf"{{\small {generado:%d.%m.%Y} "
            rf"\enspace|\enspace {hora} "
            rf"\enspace|\enspace {periodo}}}"
        ),
        r"\end{center}",
        "",
        r"\vspace{8pt}",
        (
            r"\panelSesiones"
            f"{{{referencia['semana']}}}"
            f"{{{referencia['sesion']}}}"
            f"{{{fecha_estado(referencia['fecha'])}}}"
            f"{{{proxima_semana}}}"
            f"{{{proxima_numero}}}"
            f"{{{proxima_fecha}}}"
        ),
        r"\vspace{14pt}",
        r"\cabeceraApartado{Sesión Actual (Finalizada)}",
        r"\vspace{7pt}",
        escapar_latex(situacion),
        r"\par\vspace{16pt}",
        r"\cabeceraApartado{Sesión Próxima: Generalidades}",
        r"\vspace{7pt}",
    ]

    if siguiente is None:
        lineas.append(
            "La próxima sesión no está registrada en el calendario."
        )
    else:
        lineas.append(
            escapar_latex(proxima.get("enfoque", ""))
        )
    lineas.extend(
        [
            r"\end{fichaestado}",
            r"\newpage",
            r"\begin{fichaestado}",
            r"\cabeceraApartado{Sesión Próxima: Notas}",
            r"\vspace{7pt}",
            *lista_latex(proxima.get("preparacion", [])),
            r"\par\vspace{12pt}",
            r"\cabeceraApartado{Otros avisos}",
            r"\vspace{7pt}",
            *lista_latex(proxima.get("avisos", [])),
            r"\end{fichaestado}",
        ]
    )

    return "\n".join(lineas) + "\n"



def escribir_atomico(ruta: Path, contenido: str) -> None:
    """Escribe una salida completa sin dejar archivos parciales."""

    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(
        contenido,
        encoding="utf-8",
        newline="\n",
    )
    temporal.replace(ruta)


def generar() -> Path:
    """Valida el estado y genera su fragmento LaTeX."""

    edicion = cronograma.leer_edicion_activa()
    sesiones = cronograma.obtener_sesiones(edicion)
    estado = cargar_estado(edicion)
    generado = datetime.now().astimezone()
    referencia, siguiente = localizar_sesiones(estado, sesiones)

    BUILD.mkdir(parents=True, exist_ok=True)
    ruta_latex = BUILD / "estado-contenido.tex"

    escribir_atomico(
        ruta_latex,
        crear_latex(estado, referencia, siguiente, generado),
    )

    print(
        "Estado validado: "
        f"semana {referencia['semana']}, "
        f"sesión {referencia['sesion']}."
    )

    return ruta_latex


def main() -> None:
    """Permite generar el estado por separado."""

    ruta = generar()
    print(f"Generado: {ruta.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
