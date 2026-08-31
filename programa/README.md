# Programa y documentos públicos

Esta carpeta contiene los documentos principales del curso.

## Documentos

- `programa.tex`: ensambla las secciones estables del programa.
- `cronograma.tex`: presenta la tabla generada desde los TOML de la edición activa.
- `estado-del-curso.tex`: presenta la ficha generada desde el estado operativo.
- `secciones/`: contenido académico estable del programa.

## Qué se edita

El programa se modifica en `secciones/*.tex`. El cronograma y el estado no se rellenan manualmente dentro de sus documentos principales:

- cronograma: `ediciones/<periodo>/cronograma/*.toml`;
- estado: `ediciones/<periodo>/operacion/estado.toml`.

`scripts/build.py` genera los fragmentos, compila los tres documentos y actualiza `dist/` solo si todo termina correctamente.

## LaTeX

Los comentarios incluidos en los `.tex` forman parte del carácter didáctico de la plantilla y conviene conservarlos al adaptar el diseño.
