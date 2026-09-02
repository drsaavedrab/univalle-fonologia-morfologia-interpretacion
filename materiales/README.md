
# Materiales

Esta carpeta contiene el banco de materiales docentes reutilizables del curso.

Los materiales se organizan por tema, no por semana ni por periodo:

```text
materiales/
├── transitividad/
├── construcciones-con-se/
└── topico-y-foco/
```

Cada tema puede contener:

- presentaciones;
- handouts;
- guías;
- hojas de estudio;
- ejemplos comentados;
- recursos gráficos;
- conjuntos de datos.

La edición determina cuándo se utiliza y dónde se publica cada material, pero no almacena una copia de su fuente.

## Fuentes DOCX y PDF publicados

Un DOCX puede versionarse como fuente reutilizable. Git conserva cada versión completa, aunque no muestra diferencias de párrafos ni permite fusionar cómodamente cambios simultáneos. Los PDF derivados se generan en `dist/` y no se incorporan al historial.

La selección se declara dentro de una categoría de `ediciones/<periodo>/publicacion.json` mediante `conversiones`. `scripts/materiales.py` convierte las fuentes y `scripts/publicar.py` prepara automáticamente los PDF antes de simular o aplicar la publicación.

```text
materiales/<tema>/handout.docx
        ↓ selección semestral en publicacion.json
        ↓ conversión automática
 dist/materiales/<semana>/handout.pdf
        ↓ publicación controlada
 Drive/03_Materiales/Semana <n>/
```

Los materiales estrictamente exclusivos de una edición podrán almacenarse dentro de esa edición cuando exista un caso real.