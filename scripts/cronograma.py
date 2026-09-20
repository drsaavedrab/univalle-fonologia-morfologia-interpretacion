"""
Genera la tabla LaTeX del cronograma de la edición activa.

Fuentes editables:

- ediciones/<periodo>/cronograma/calendario.toml
- ediciones/<periodo>/cronograma/contenidos.toml
- bibliografia/referencias.bib

Salida automática:

- build/cronograma-contenido.tex
"""

from __future__ import annotations

import argparse
import re
import tomllib
import unicodedata
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
BUILD = RAIZ / "build"
ARCHIVO_EDICION = RAIZ / "config" / "edicion-activa.tex"
ARCHIVO_BIB = RAIZ / "bibliografia" / "referencias.bib"

DIAS = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "domingo": 6,
}

MESES = {
    1: "ene.",
    2: "feb.",
    3: "mar.",
    4: "abr.",
    5: "may.",
    6: "jun.",
    7: "jul.",
    8: "ago.",
    9: "sep.",
    10: "oct.",
    11: "nov.",
    12: "dic.",
}

ROMANOS = {1: "I", 2: "II", 3: "III", 4: "IV"}


def normalizar(texto: str) -> str:
    """Elimina tildes y convierte el texto a minúsculas."""

    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(
        caracter
        for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    )


def leer_edicion_activa() -> str:
    """Extrae la edición activa definida en el archivo LaTeX."""

    contenido = ARCHIVO_EDICION.read_text(encoding="utf-8")
    coincidencia = re.search(
        r"\\newcommand\s*\{\s*\\edicionActiva\s*\}\s*"
        r"\{\s*([^{}]+?)\s*\}",
        contenido,
    )

    if coincidencia is None:
        raise ValueError(
            "No se pudo determinar la edición activa."
        )

    edicion = coincidencia.group(1).strip()

    if re.fullmatch(r"\d{4}-[12]", edicion) is None:
        raise ValueError(
            f"Formato de edición no válido: {edicion}"
        )

    return edicion


def carpeta_cronograma(edicion: str) -> Path:
    """Devuelve la carpeta del cronograma de una edición."""

    return RAIZ / "ediciones" / edicion / "cronograma"


def cargar_toml(ruta: Path) -> dict:
    """Carga un archivo TOML y produce un error legible."""

    if not ruta.is_file():
        raise FileNotFoundError(f"No existe {ruta}.")

    with ruta.open("rb") as archivo:
        return tomllib.load(archivo)


def validar_calendario(configuracion: dict) -> None:
    """Valida las propiedades básicas del calendario."""

    inicio = configuracion.get("inicio")
    fin = configuracion.get("fin")

    if not isinstance(inicio, date) or not isinstance(fin, date):
        raise ValueError(
            "inicio y fin deben escribirse como fechas TOML."
        )

    if inicio > fin:
        raise ValueError(
            "La fecha inicial es posterior a la fecha final."
        )

    if normalizar(configuracion.get("inicio_semana", "")) != "lunes":
        raise ValueError(
            "Por ahora, inicio_semana debe ser «lunes»."
        )

    dias = configuracion.get("dias_clase", [])

    if not dias:
        raise ValueError("dias_clase no puede estar vacío.")

    desconocidos = [
        dia for dia in dias
        if normalizar(dia) not in DIAS
    ]

    if desconocidos:
        raise ValueError(
            "Días desconocidos: " + ", ".join(desconocidos)
        )


def generar_sesiones(configuracion: dict) -> list[dict]:
    """
    Calcula semana, sesión, fecha, modalidad y nota.

    Una excepción cambia la modalidad, pero no elimina la sesión.
    """

    validar_calendario(configuracion)

    inicio: date = configuracion["inicio"]
    fin: date = configuracion["fin"]
    dias_clase = {
        DIAS[normalizar(dia)]
        for dia in configuracion["dias_clase"]
    }
    excepciones = {
        excepcion["fecha"]: excepcion
        for excepcion in configuracion.get("excepciones", [])
    }

    lunes_inicial = inicio - timedelta(days=inicio.weekday())
    fechas_por_semana: dict[int, list[date]] = defaultdict(list)
    fecha_actual = inicio

    while fecha_actual <= fin:
        if fecha_actual.weekday() in dias_clase:
            semana = (
                (fecha_actual - lunes_inicial).days // 7
            ) + 1
            fechas_por_semana[semana].append(fecha_actual)

        fecha_actual += timedelta(days=1)

    sesiones: list[dict] = []

    for semana in sorted(fechas_por_semana):
        for posicion, fecha_sesion in enumerate(
            sorted(fechas_por_semana[semana]),
            start=1,
        ):
            if posicion not in ROMANOS:
                raise ValueError(
                    f"Demasiadas sesiones en la semana {semana}."
                )

            excepcion = excepciones.get(fecha_sesion, {})

            sesiones.append(
                {
                    "semana": semana,
                    "sesion": ROMANOS[posicion],
                    "fecha": fecha_sesion,
                    "modalidad": excepcion.get(
                        "modalidad",
                        "presencial",
                    ),
                    "nota": excepcion.get("nota", "").strip(),
                }
            )

    fechas_validas = {sesion["fecha"] for sesion in sesiones}
    excepciones_invalidas = set(excepciones) - fechas_validas

    if excepciones_invalidas:
        detalle = ", ".join(
            fecha.isoformat()
            for fecha in sorted(excepciones_invalidas)
        )
        raise ValueError(
            "Excepciones fuera de los días de clase: " + detalle
        )

    return sesiones


def obtener_sesiones(edicion: str) -> list[dict]:
    """Carga el calendario de una edición y genera sus sesiones."""

    ruta = carpeta_cronograma(edicion) / "calendario.toml"
    return generar_sesiones(cargar_toml(ruta))


def claves_bibliograficas() -> set[str]:
    """Extrae y valida las claves declaradas en referencias.bib."""

    contenido = ARCHIVO_BIB.read_text(encoding="utf-8")
    claves = re.findall(
        r"@\w+\s*\{\s*([^,\s]+)\s*,",
        contenido,
        flags=re.IGNORECASE,
    )

    duplicadas = {
        clave for clave in claves
        if claves.count(clave) > 1
    }

    if duplicadas:
        raise ValueError(
            "Claves bibliográficas duplicadas: "
            + ", ".join(sorted(duplicadas))
        )

    return set(claves)


def abreviar_fechas(fechas: list[date]) -> str:
    """Produce «2 sep.» o «2 y 4 sep.»."""

    if len(fechas) == 1:
        fecha = fechas[0]
        return f"{fecha.day} {MESES[fecha.month]}"

    if len(fechas) == 2 and fechas[0].month == fechas[1].month:
        return (
            f"{fechas[0].day} y {fechas[1].day} "
            f"{MESES[fechas[0].month]}"
        )

    return " y ".join(
        f"{fecha.day} {MESES[fecha.month]}"
        for fecha in fechas
    )


def formatear_lecturas(
    fila: dict,
    claves_validas: set[str],
) -> str:
    """Convierte lecturas estructuradas en comandos LaTeX."""

    sin_lectura = fila.get("sin_lectura")
    lecturas = fila.get("lecturas", [])

    if sin_lectura and lecturas:
        raise ValueError(
            "Una fila no puede tener lecturas y sin_lectura."
        )

    if sin_lectura:
        opciones = {
            "adicional": r"\sinLecturaAdicional",
            "asignada": r"\sinLecturaAsignada",
        }

        if sin_lectura not in opciones:
            raise ValueError(
                f"Valor sin_lectura desconocido: {sin_lectura}"
            )

        return opciones[sin_lectura]

    if not lecturas:
        raise ValueError(
            "Cada fila debe declarar lecturas o sin_lectura."
        )

    categorias_validas = {"obligatoria", "complementaria"}
    categorias = [lectura.get("categoria") for lectura in lecturas]

    desconocidas = set(categorias) - categorias_validas

    if desconocidas:
        raise ValueError(
            "Categorías de lectura desconocidas: "
            + ", ".join(sorted(desconocidas))
        )

    lineas: list[str] = []

    for categoria in ("obligatoria", "complementaria"):
        grupo = [
            lectura
            for lectura in lecturas
            if lectura["categoria"] == categoria
        ]

        if not grupo:
            continue

        if categoria == "obligatoria":
            etiqueta = (
                r"\lecturaObligatoria"
                if len(grupo) == 1
                else r"\lecturasObligatorias"
            )
        else:
            etiqueta = r"\lecturaComplementaria"


        lineas.append(etiqueta)

        for lectura in grupo:
            clave = lectura.get("clave", "").strip()

            if clave not in claves_validas:
                raise ValueError(
                    f"La clave «{clave}» no existe en referencias.bib."
                )

            detalle = lectura.get("detalle", "").strip()

            if detalle:
                cita = rf"\citalectura[{detalle}]{{{clave}}}."
            else:
                cita = rf"\citalectura{{{clave}}}."

            lineas.append(cita)

    return "\n".join(lineas)


def preparar_filas(
    filas: list[dict],
    sesiones: list[dict],
) -> list[dict]:
    """Vincula contenidos, fechas y referencias bibliográficas."""

    indice = {
        (sesion["semana"], sesion["sesion"]): sesion
        for sesion in sesiones
    }
    utilizadas: set[tuple[int, str]] = set()
    claves_validas = claves_bibliograficas()
    resultado: list[dict] = []

    for fila in filas:
        semana = fila.get("semana")
        nombres = fila.get("sesiones", [])

        if not isinstance(semana, int) or not nombres:
            raise ValueError(
                "Cada [[filas]] necesita semana y sesiones."
            )

        fechas: list[date] = []

        for nombre in nombres:
            clave_sesion = (semana, nombre)

            if clave_sesion not in indice:
                raise ValueError(
                    f"No existe la sesión {semana}-{nombre}."
                )

            if clave_sesion in utilizadas:
                raise ValueError(
                    f"La sesión {semana}-{nombre} está duplicada."
                )

            utilizadas.add(clave_sesion)
            fechas.append(indice[clave_sesion]["fecha"])

        tema = fila.get("tema", "").strip()
        actividad = fila.get("actividad", "").strip()

        if not tema or not actividad:
            raise ValueError(
                f"Tema o actividad vacíos en la semana {semana}."
            )

        resultado.append(
            {
                "semana": semana,
                "sesiones": "--".join(nombres),
                "fecha": abreviar_fechas(fechas),
                "tema": tema,
                "lecturas": formatear_lecturas(
                    fila,
                    claves_validas,
                ),
                "actividad": actividad,
            }
        )

    faltantes = set(indice) - utilizadas

    if faltantes:
        detalle = ", ".join(
            f"{semana}-{sesion}"
            for semana, sesion in sorted(faltantes)
        )
        raise ValueError(
            "Sesiones sin contenido: " + detalle
        )

    return resultado


def crear_latex(
    edicion: str,
    filas: list[dict],
    mostrar_sesion: bool = True,
) -> str:
    """Construye la tabla longtable con sesión visible u oculta."""

    lineas = [
        "% Generado automáticamente. No editar.",
        f"% Edición: {edicion}",
        "",
        r"\begingroup",
        r"\small",
        r"\renewcommand{\arraystretch}{1.25}",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{longtable}{@{}",
    ]

    if mostrar_sesion:
        lineas.extend(
            [
                r"    >{\centering\arraybackslash}p{0.055\textwidth}",
                r"    >{\centering\arraybackslash}p{0.045\textwidth}",
                r"    >{\centering\arraybackslash}p{0.075\textwidth}",
                r"    >{\raggedright\arraybackslash}p{0.225\textwidth}",
                r"    >{\raggedright\arraybackslash}p{0.395\textwidth}",
                r"    >{\raggedleft\arraybackslash}p{0.15\textwidth}",
                r"@{}}",
            ]
        )
        encabezado = [
            r"\textbf{Semana} & \textbf{Sesión} & \textbf{Fecha} &",
            r"\textbf{Tema} & \textbf{Lecturas} & \textbf{Actividad} \\",
        ]
        numero_columnas = 6
    else:
        lineas.extend(
            [
                r"    >{\centering\arraybackslash}p{0.055\textwidth}",
                r"    >{\centering\arraybackslash}p{0.075\textwidth}",
                r"    >{\raggedright\arraybackslash}p{0.225\textwidth}",
                r"    >{\raggedright\arraybackslash}p{0.425\textwidth}",
                r"    >{\raggedleft\arraybackslash}p{0.18\textwidth}",
                r"@{}}",
            ]
        )
        encabezado = [
            r"\textbf{Semana} & \textbf{Fecha} & \textbf{Tema} &",
            r"\textbf{Lecturas} & \textbf{Actividad} \\",
        ]
        numero_columnas = 5

    lineas.extend(
        [
            r"\toprule",
            *encabezado,
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            *encabezado,
            r"\midrule",
            r"\endhead",
            r"\midrule",
            (
                rf"\multicolumn{{{numero_columnas}}}{{r}}"
                r"{\small Continúa en la página siguiente.} \\"
            ),
            r"\endfoot",
            r"\bottomrule",
            r"\endlastfoot",
            "",
        ]
    )

    semana_anterior: int | None = None

    for fila in filas:
        if semana_anterior is not None:
            lineas.extend(
                [
                    "",
                    (
                        r"\addlinespace[4pt]"
                        if fila["semana"] == semana_anterior
                        else r"\midrule"
                    ),
                    "",
                ]
            )

        semana_visible = (
            ""
            if fila["semana"] == semana_anterior
            else str(fila["semana"])
        )

        valores = [semana_visible]
        if mostrar_sesion:
            valores.append(fila["sesiones"])
        valores.extend(
            [
                fila["fecha"],
                fila["tema"],
                fila["lecturas"],
                fila["actividad"],
            ]
        )
        lineas.extend(
            [
                f"{valor} &" if indice < len(valores) - 1 else valor
                for indice, valor in enumerate(valores)
            ]
        )
        lineas.append(r"\\")

        semana_anterior = fila["semana"]

    lineas.extend(
        [
            "",
            r"\end{longtable}",
            r"\endgroup",
            "",
        ]
    )

    return "\n".join(lineas)


def generar() -> Path:
    """Valida las fuentes y genera la tabla en build/."""

    edicion = leer_edicion_activa()
    configuracion_calendario = cargar_toml(
        carpeta_cronograma(edicion) / "calendario.toml"
    )
    sesiones = generar_sesiones(configuracion_calendario)
    mostrar_sesion = configuracion_calendario.get(
        "mostrar_sesion",
        True,
    )
    if not isinstance(mostrar_sesion, bool):
        raise ValueError("mostrar_sesion debe ser true o false.")

    contenidos = cargar_toml(
        carpeta_cronograma(edicion) / "contenidos.toml"
    ).get("filas", [])

    if not contenidos:
        raise ValueError(
            "contenidos.toml no contiene ninguna [[filas]]."
        )

    filas = preparar_filas(contenidos, sesiones)
    BUILD.mkdir(parents=True, exist_ok=True)
    destino = BUILD / "cronograma-contenido.tex"
    temporal = destino.with_suffix(".tex.tmp")
    temporal.write_text(
        crear_latex(edicion, filas, mostrar_sesion),
        encoding="utf-8",
        newline="\n",
    )
    temporal.replace(destino)

    print(
        f"Cronograma validado: {len(sesiones)} sesiones, "
        f"{len(filas)} filas académicas."
    )

    return destino


def cargar_argumentos() -> argparse.Namespace:
    """Lee las opciones del generador de cronograma."""

    parser = argparse.ArgumentParser(
        description="Valida y genera el cronograma de la edición activa."
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Elimina solo el fragmento LaTeX generado y termina.",
    )
    return parser.parse_args()


def limpiar() -> None:
    """Retira únicamente las salidas que este generador administra."""

    destinos = [
        BUILD / "cronograma-contenido.tex",
        BUILD / "cronograma-contenido.tex.tmp",
    ]
    existentes = [ruta for ruta in destinos if ruta.is_file() or ruta.is_symlink()]

    if not existentes:
        print("Nada que limpiar: no hay fragmentos de cronograma generados.")
        return

    for ruta in existentes:
        if ruta.parent.resolve() != BUILD.resolve():
            raise SystemExit(f"Error: ruta de limpieza inesperada: {ruta}")
        print(f"Eliminando: {ruta.relative_to(RAIZ)}")
        ruta.unlink()

    print("Limpieza del cronograma completada.")


def main() -> None:
    """Permite validar, generar o limpiar el cronograma por separado."""

    argumentos = cargar_argumentos()
    if argumentos.clean:
        limpiar()
        return

    destino = generar()
    print(f"Generado: {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
