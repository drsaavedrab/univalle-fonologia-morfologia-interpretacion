
#!/usr/bin/env python3

"""Publica en Google Drive los archivos de la edición activa."""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import materiales


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
        "--clean",
        action="store_true",
        help=(
            "Sincroniza las categorías seleccionadas y mueve "
            "los sobrantes a 09_Archivo. Sin --apply solo simula."
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


def validar_ruta_remota(ruta, etiqueta):
    """Rechaza destinos vacíos, absolutos o capaces de escapar."""

    if not isinstance(ruta, str) or not ruta.strip():
        sys.exit(f"ERROR: la ruta remota '{etiqueta}' está vacía.")

    partes = [parte for parte in ruta.replace("\\", "/").split("/") if parte]
    if ruta.startswith(("/", "\\")) or any(
        parte in {".", ".."} for parte in partes
    ):
        sys.exit(f"ERROR: ruta remota no válida en '{etiqueta}': {ruta}")

    if len(partes) < 4:
        sys.exit(
            f"ERROR: la ruta remota '{etiqueta}' es demasiado amplia: {ruta}"
        )

    return "/".join(partes)


def ejecutar_publicacion(
    remoto,
    publicacion,
    origen,
    aplicar,
    limpiar,
    carpeta_archivo,
):
    """Copia o sincroniza una categoría mediante rclone."""

    destino = validar_ruta_remota(publicacion["destino"], "destino")
    destino_remoto = f"{remoto}:{destino}"
    operacion = "sync" if limpiar else "copy"

    comando = [
        "rclone",
        operacion,
        str(origen),
        destino_remoto,
        "--files-from",
        "-",
        "--verbose",
    ]

    archivo_remoto = None
    if limpiar:
        archivo = validar_ruta_remota(carpeta_archivo, "archivo")
        marca = datetime.now().strftime("%Y%m%d-%H%M%S")
        archivo_remoto = f"{remoto}:{archivo}/{publicacion['nombre']}/{marca}"
        if archivo_remoto == destino_remoto:
            sys.exit("ERROR: el archivo remoto coincide con el destino.")
        comando.extend(
            [
                "--delete-excluded",
                "--backup-dir",
                archivo_remoto,
                "--max-delete",
                "20",
            ]
        )

    if not aplicar:
        comando.append("--dry-run")

    print()
    print("=" * 60)
    print(f"Categoría: {publicacion['nombre']}")
    print(f"Origen:    {origen}")
    print(f"Destino:   {destino_remoto}")
    print(f"Operación: {operacion}")
    if archivo_remoto:
        print(f"Archivo:   {archivo_remoto}")
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

    # Las categorías pueden declarar conversiones DOCX→PDF.
    # La preparación sucede también durante la simulación, pero solo
    # modifica salidas locales ignoradas dentro de dist/.
    try:
        resultados_materiales = materiales.preparar_publicaciones(
            publicaciones
        )
    except materiales.ErrorMaterial as error:
        sys.exit(f"ERROR: no se pudieron preparar los materiales: {error}")

    if resultados_materiales:
        print("Preparando materiales de la edición activa:")
        materiales.mostrar_resultados(resultados_materiales)

    if argumentos.apply:
        if argumentos.clean:
            print(
                "MODO SINCRONIZACIÓN: los sobrantes se moverán a 09_Archivo."
            )
        else:
            print("MODO PUBLICACIÓN: Google Drive será actualizado.")
    else:
        print("MODO SIMULACIÓN: Google Drive no será modificado.")
        if argumentos.clean:
            print("Se simulará también la limpieza administrada.")

    print(f"Edición activa: {edicion}")

    for publicacion in publicaciones:
        origen = validar_publicacion(publicacion)

        ejecutar_publicacion(
            configuracion["remoto"],
            publicacion,
            origen,
            argumentos.apply,
            argumentos.clean,
            configuracion.get("archivo", ""),
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