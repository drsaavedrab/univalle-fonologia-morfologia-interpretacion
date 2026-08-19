
# Plantilla de repositorio docente

Plantilla para crear repositorios de cursos con:

- fuentes LaTeX;
- separación entre contenido estable y ediciones;
- bibliografía con BibLaTeX;
- compilación automatizada;
- publicación segura en Google Drive;
- bancos reutilizables de actividades y materiales.

## Antes de utilizarla

Debe reemplazarse:

- `AAAA-P` por el periodo académico;
- la información de `config/curso.tex`;
- los datos de `ediciones/<periodo>/semestre.tex`;
- las rutas de `publicacion.json`;
- la identidad institucional;
- el contenido académico heredado o provisional.

La plantilla no debe publicarse ni utilizarse directamente sin completar estos datos.

## Organización

- `config/`: identidad del curso y edición activa.
- `programa/`: documentos principales y secciones académicas.
- `bibliografia/`: referencias del curso.
- `actividades/`: banco reutilizable de actividades.
- `materiales/`: banco reutilizable de materiales.
- `ediciones/`: información propia de cada periodo.
- `recursos/`: identidad gráfica.
- `scripts/`: compilación y publicación.
- `build/`: archivos técnicos generados.
- `dist/`: PDF destinados a publicación.

## Compilación

```bash
python scripts/build.py
```

## Publicación

Simulación:

```bash
python scripts/publicar.py
```

Publicación real:

```bash
python scripts/publicar.py --apply
```

## Información privada

Las listas de estudiantes, calificaciones y entregas deben permanecer fuera del repositorio, dentro de `Teaching/Private/` y del área privada correspondiente de Google Drive.