# Plantilla de repositorio docente

Infraestructura reutilizable para administrar un curso académico estable a través de varios periodos, generar documentos con LaTeX, registrar la operación del semestre y publicar entregables en Google Drive.

## Tres usos distintos

- **Curso nuevo:** crea otro repositorio a partir de esta plantilla.
- **Periodo nuevo:** añade una edición dentro del repositorio del mismo curso.
- **Curso en marcha:** actualiza estado, cronograma, materiales y publicaciones durante el semestre.

Las instrucciones completas están en `manuales/`.

## Estructura

- `config/`: identidad estable y selección de la edición activa.
- `programa/`: documentos principales y secciones estables del programa.
- `bibliografia/`: base BibTeX compartida.
- `correos/`: plantillas versionadas de comunicaciones.
- `actividades/`: banco reutilizable de actividades.
- `materiales/`: banco reutilizable de materiales por tema.
- `ediciones/`: calendario, contenidos, estado, bitácora y publicación de cada periodo.
- `recursos/`: identidad y recursos compartidos.
- `manuales/`: implementación y operación.
- `notas/`: decisiones internas que no pertenecen a un periodo.
- `scripts/`: generación, compilación, limpieza y publicación.
- `build/`: auxiliares automáticos; no se editan.
- `dist/`: PDF finales generados; no se editan.

## Fuentes y salidas

| Fuente editable | Salida automática |
|---|---|
| `programa/secciones/*.tex` | `dist/programa.pdf` |
| `cronograma/calendario.toml` + `cronograma/contenidos.toml` + `.bib` | `dist/cronograma.pdf` |
| `operacion/estado.toml` + calendario | `dist/estado-del-curso.pdf` |
| `operacion/bienvenida.toml` + `estado.toml` + plantillas | `build/correos/*.txt` |

## Edición activa

`config/edicion-activa.tex` contiene el único selector global del periodo. La carpeta correspondiente debe existir dentro de `ediciones/`.

## Comandos principales

```bash
python scripts/build.py
python scripts/correos.py --only bienvenida
python scripts/correos.py --only aviso-posclase
python scripts/publicar.py
python scripts/publicar.py --apply
```

Para limpiar auxiliares y reconstruir:

```bash
python scripts/build.py --clean
python scripts/build.py
```

## Seguridad

- La simulación es el comportamiento predeterminado de publicación.
- `--clean --apply` archiva sobrantes en `09_Archivo` y limita los retiros.
- Las credenciales de rclone nunca se guardan en Git.
- Listas, correos, notas, entregas y demás información estudiantil permanecen en `Teaching/Private/`.

## Manuales

1. `manuales/01-crear-curso.md`
2. `manuales/02-nuevo-periodo.md`
3. `manuales/03-operacion-cotidiana.md`

Empieza por el manual que corresponda al tipo de trabajo; no mezcles la creación de un curso con la apertura de un periodo.
