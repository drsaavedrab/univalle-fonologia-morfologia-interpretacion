
#!/usr/bin/env python3

"""
Compila el programa y el cronograma del curso.

Los archivos técnicos producidos por LaTeX se guardan en build/.
Los PDF finales destinados a publicación se copian a dist/.
"""

from pathlib import Path
import shutil
import subprocess
import sys


# ------------------------------------------------------------
# RUTAS DEL REPOSITORIO
# ------------------------------------------------------------

# __file__ representa este archivo: scripts/build.py
#
# .resolve() obtiene su ruta absoluta.
#
# .parent obtiene scripts/.
#
# .parent.parent obtiene la raíz del repositorio.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Carpeta donde están programa.tex y cronograma.tex.
PROGRAM_DIR = REPO_ROOT / "programa"

# Carpeta para los archivos técnicos de LaTeX.
BUILD_DIR = REPO_ROOT / "build"

# Carpeta que contendrá exclusivamente los PDF publicables.
DIST_DIR = REPO_ROOT / "dist"


# ------------------------------------------------------------
# DOCUMENTOS QUE SE COMPILARÁN
# ------------------------------------------------------------

# Cada nombre corresponde a un archivo .tex dentro de programa/.
DOCUMENTS = (
    "programa",
    "cronograma",
)


def verify_dependencies() -> None:
    """Comprueba que latexmk esté disponible en el sistema."""

    # shutil.which busca la aplicación en las rutas del sistema.
    if shutil.which("latexmk") is None:
        print(
            "Error: no se encontró latexmk.\n"
            "Comprueba que TeX Live esté instalado y disponible "
            "desde la terminal.",
            file=sys.stderr,
        )
        raise SystemExit(1)


def prepare_directories() -> None:
    """Crea build/ y dist/ si todavía no existen."""

    # parents=True permite crear carpetas superiores si hiciera falta.
    #
    # exist_ok=True evita un error cuando la carpeta ya existe.
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def compile_document(document: str) -> Path:
    """Compila un documento y devuelve la ruta de su PDF."""

    source_file = PROGRAM_DIR / f"{document}.tex"
    generated_pdf = BUILD_DIR / f"{document}.pdf"

    # Verifica que exista el documento fuente antes de compilar.
    if not source_file.exists():
        print(
            f"Error: no existe {source_file}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(f"Compilando {source_file.name}...")

    # Ejecuta latexmk desde programa/ para conservar correctamente
    # las rutas relativas utilizadas por los documentos.
    subprocess.run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "-outdir=../build",
            source_file.name,
        ],
        cwd=PROGRAM_DIR,
        check=True,
    )

    # Comprueba que efectivamente se haya generado el PDF.
    if not generated_pdf.exists():
        print(
            f"Error: la compilación no produjo {generated_pdf}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    return generated_pdf


def publish_documents(generated_documents: dict[str, Path]) -> None:
    """Copia a dist/ únicamente un conjunto completo y válido."""

    temporary_files: dict[str, Path] = {}

    try:
        # Primero prepara todas las copias temporales.
        # Si una copia falla, ningún PDF publicado se reemplaza.
        for document, generated_pdf in generated_documents.items():
            temporary_pdf = DIST_DIR / f".{document}.pdf.tmp"
            shutil.copyfile(generated_pdf, temporary_pdf)
            temporary_files[document] = temporary_pdf

        # Solo después de preparar todo se reemplazan los entregables.
        for document, temporary_pdf in temporary_files.items():
            destination_pdf = DIST_DIR / f"{document}.pdf"

            # replace sustituye el destino y funciona tanto en
            # Windows como en Linux.
            temporary_pdf.replace(destination_pdf)

            print(f"Publicado localmente: dist/{destination_pdf.name}")

    finally:
        # Retira cualquier temporal que haya quedado por un error.
        for temporary_pdf in temporary_files.values():
            if temporary_pdf.exists():
                temporary_pdf.unlink()


def main() -> None:
    """Ejecuta la compilación y publicación local."""

    verify_dependencies()
    prepare_directories()

    generated_documents: dict[str, Path] = {}

    # Compila todos los documentos antes de modificar dist/.
    for document in DOCUMENTS:
        generated_documents[document] = compile_document(document)

    # Publica solamente si todas las compilaciones terminaron bien.
    publish_documents(generated_documents)

    print()
    print("Compilación completada correctamente.")
    print("Entregables:")
    print("  dist/programa.pdf")
    print("  dist/cronograma.pdf")


# Este condicional ejecuta main() solamente cuando abrimos este
# archivo como programa, no cuando se importa desde otro módulo.
if __name__ == "__main__":
    main()