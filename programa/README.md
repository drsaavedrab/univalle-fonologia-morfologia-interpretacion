
# Programa y cronograma

Esta carpeta contiene los documentos principales compilables del curso.

## Documentos principales

- `programa.tex`: construye el programa de asignatura.
- `cronograma.tex`: construye el cronograma de la edición activa.

Ambos documentos incorporan:

- los datos estables definidos en `config/curso.tex`;
- la edición seleccionada en `config/edicion-activa.tex`;
- los datos particulares almacenados dentro de `ediciones/`;
- la bibliografía registrada en `bibliografia/referencias.bib`.

## Secciones del programa

La carpeta `secciones/` divide el programa en componentes académicos editables:

- descripción;
- objetivos;
- metodología;
- contenidos;
- evaluación;
- bibliografía;
- políticas.

## Compilación

La compilación oficial se ejecuta desde la raíz del repositorio:

```bash
python scripts/build.py
```

Los archivos técnicos se guardan en `build/` y los PDF finales en `dist/`.