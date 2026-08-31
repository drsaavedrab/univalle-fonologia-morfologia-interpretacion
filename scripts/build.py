#!/usr/bin/env python3
"""Genera y compila todos los documentos públicos del curso."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess

import cronograma
import correos
import estado

REPO_ROOT = Path(__file__).resolve().parent.parent
PROGRAM_DIR = REPO_ROOT / "programa"
BUILD_DIR = REPO_ROOT / "build"
DIST_DIR = REPO_ROOT / "dist"
DOCUMENTS = ("programa", "cronograma", "estado-del-curso")


def parse_arguments() -> argparse.Namespace:
    """Lee las opciones del flujo local."""
    parser = argparse.ArgumentParser(
        description="Genera y compila los documentos públicos del curso."
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Elimina únicamente los auxiliares de build/ y termina.",
    )
    return parser.parse_args()


def clean_build() -> None:
    """Vacía build/ de forma acotada y conserva su .gitkeep."""
    root = REPO_ROOT.resolve()
    target = BUILD_DIR.resolve()

    if target.parent != root or target.name != "build":
        raise SystemExit(f"Error: ruta de limpieza inesperada: {target}")

    if not BUILD_DIR.exists():
        print("Nada que limpiar: build/ no existe.")
        return

    if BUILD_DIR.is_symlink() or (
        hasattr(os.path, "isjunction") and os.path.isjunction(BUILD_DIR)
    ):
        raise SystemExit("Error: build/ es un enlace o una unión; no se limpia.")

    targets = [item for item in BUILD_DIR.iterdir() if item.name != ".gitkeep"]
    if not targets:
        print("Nada que limpiar: build/ ya está vacío.")
        return

    print("Se eliminarán únicamente estos auxiliares de build/:")
    for item in targets:
        print(f"  - {item.relative_to(REPO_ROOT)}")

    for item in targets:
        if item.is_symlink() or (
            hasattr(os.path, "isjunction") and os.path.isjunction(item)
        ):
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print("Limpieza local completada; dist/ no fue modificado.")


def verify_dependencies() -> None:
    """Comprueba que LaTeX esté disponible."""
    if shutil.which("latexmk") is None:
        raise SystemExit(
            "Error: no se encontró latexmk. Comprueba la instalación de TeX Live."
        )


def prepare_directories() -> None:
    """Crea las carpetas de salida si todavía no existen."""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def generate_sources() -> None:
    """Genera los fragmentos variables de la edición activa."""
    print("Generando cronograma desde TOML...")
    cronograma.generar()
    print("Generando estado operativo...")
    estado.generar()
    print("Generando borradores de correo...")
    correos.generar()


def compile_document(document: str) -> Path:
    """Compila un documento y devuelve la ruta del PDF producido."""
    source_file = PROGRAM_DIR / f"{document}.tex"
    # Cada documento conserva sus auxiliares en un subdirectorio
    # independiente. Esto evita colisiones y archivos .aux corruptos
    # al compilar varios documentos consecutivamente en Windows.
    document_build_dir = BUILD_DIR / document
    document_build_dir.mkdir(parents=True, exist_ok=True)
    generated_pdf = document_build_dir / f"{document}.pdf"
    if not source_file.is_file():
        raise SystemExit(f"Error: no existe {source_file}")

    print(f"Compilando {source_file.name}...")
    subprocess.run(
        [
            "latexmk", "-pdf", "-interaction=nonstopmode",
            "-halt-on-error", "-file-line-error",
            f"-outdir=../build/{document}", source_file.name,
        ],
        cwd=PROGRAM_DIR,
        check=True,
    )
    if not generated_pdf.is_file():
        raise SystemExit(f"Error: la compilación no produjo {generated_pdf}")
    return generated_pdf


def publish_locally(generated_documents: dict[str, Path]) -> None:
    """Actualiza dist/ conjuntamente; esto todavía no toca Google Drive."""
    temporary_files: dict[str, Path] = {}
    try:
        for document, generated_pdf in generated_documents.items():
            temporary_pdf = DIST_DIR / f".{document}.pdf.tmp"
            shutil.copyfile(generated_pdf, temporary_pdf)
            temporary_files[document] = temporary_pdf

        for document, temporary_pdf in temporary_files.items():
            destination_pdf = DIST_DIR / f"{document}.pdf"
            temporary_pdf.replace(destination_pdf)
            print(f"Publicado localmente: dist/{destination_pdf.name}")
    finally:
        for temporary_pdf in temporary_files.values():
            if temporary_pdf.exists():
                temporary_pdf.unlink()


def main() -> None:
    """Ejecuta el flujo local completo, sin modificar Google Drive."""
    arguments = parse_arguments()
    if arguments.clean:
        clean_build()
        return

    verify_dependencies()
    prepare_directories()
    generate_sources()

    generated_documents: dict[str, Path] = {}
    for document in DOCUMENTS:
        generated_documents[document] = compile_document(document)

    publish_locally(generated_documents)

    print("\nCompilación completada correctamente.")
    print("Entregables:")
    for document in DOCUMENTS:
        print(f"  dist/{document}.pdf")
    print("Borrador operativo:")
    print("  build/correos/bienvenida.txt")
    print("  build/correos/aviso-posclase.txt")


if __name__ == "__main__":
    main()
