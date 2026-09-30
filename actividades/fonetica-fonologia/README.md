# Ejercicios de fonética y fonología

`contenido.tex` es la fuente editable y reutilizable de los cinco ejercicios. Conserva las consignas, la nota del ejercicio 2 y los cuatro pares de señas del documento recibido, con sus 15 hipervínculos (14 destinos distintos), incluidas las marcas temporales.

`recursos/fonetica-fonologia-uv.docx` conserva el original recibido como referencia de procedencia; no es una segunda fuente que deba actualizarse. Las revisiones se hacen en `contenido.tex` y se registran en Git.

El Taller 1 de `ediciones/2026-2/actividades/taller-01.tex` incorpora directamente este contenido mediante `\input`. No se copian las consignas a la edición. Para reutilizarlo, incluirlo desde otro documento que cargue `enumitem` e `hyperref`.

## Verificación inicial

Se compiló el Taller 1 y se cotejaron los 14 destinos distintos de sus enlaces PDF con las relaciones del DOCX original, incluidas las tres marcas temporales. Las cinco páginas de YouTube respondieron HTTP 200; los nueve destinos de Drive respondieron HTTP 401 en la comprobación sin sesión. Se conservaron los destinos originales: queda por confirmar el acceso a esos archivos con una cuenta de estudiante autorizada.

