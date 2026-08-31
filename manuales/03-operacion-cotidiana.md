# Manual 3 — Operación cotidiana de un curso en marcha

Esta guía es para el uso semanal del repositorio una vez iniciado el periodo. El ejemplo práctico es MSE-II, pero el flujo sirve para cualquier curso creado con esta plantilla.

## Regla principal

Edita fuentes, genera salidas y publica entregables. Nunca edites directamente `build/`, `dist/*.pdf` ni archivos que ya estén en Drive.

## Mapa rápido: qué se toca

| Necesidad | Archivo o carpeta editable |
|---|---|
| actualizar dónde está el curso y redactar el aviso posterior | `ediciones/<periodo>/operacion/estado.toml` |
| preparar el correo inicial | `ediciones/<periodo>/operacion/bienvenida.toml` |
| cambiar una fecha, modalidad o excepción | `ediciones/<periodo>/cronograma/calendario.toml` |
| cambiar tema, lectura o actividad programada | `ediciones/<periodo>/cronograma/contenidos.toml` |
| añadir una referencia | `bibliografia/referencias.bib` |
| corregir el programa estable | `programa/secciones/` |
| guardar una actividad reutilizable | `actividades/<actividad>/` |
| guardar un material reutilizable | `materiales/<tema>/` |
| anotar lo que ocurrió y pendientes | `ediciones/<periodo>/bitacora.md` |
| configurar qué llega a Drive | `ediciones/<periodo>/publicacion.json` |

## Rutina mínima antes de la próxima sesión

1. Abre `operacion/estado.toml`.
2. En `[avance]`, registra la sesión actual o la última finalizada y describe la situación en presente.
3. En `[proxima_sesion]`, escribe el enfoque, la preparación y los avisos.
4. Si corresponde, confirma el enlace de la carpeta compartida.
5. Ejecuta:

```bash
python scripts/build.py
```

6. Revisa `dist/estado-del-curso.pdf` y `build/correos/aviso-posclase.txt`.
7. Si cambió el cronograma, revisa también `dist/cronograma.pdf`.

## Correos

Las plantillas estables están en `correos/plantillas/`; normalmente no se editan durante el semestre. Los datos variables están en los TOML de la edición.

```bash
python scripts/correos.py
python scripts/correos.py --only bienvenida
python scripts/correos.py --only aviso-posclase
```

Los borradores aparecen en `build/correos/`. Deben revisarse y copiarse manualmente al cliente de correo; el repositorio no envía mensajes.
## Rutina después de clase

Actualiza `ediciones/<periodo>/bitacora.md` con tres elementos cuando sean útiles:

- qué se alcanzó a desarrollar;
- qué queda pendiente;
- ejemplos, dificultades o decisiones que conviene recordar.

No necesitas escribir una crónica extensa. Tres o cuatro líneas útiles son suficientes. No incluyas información individual de estudiantes.

## Cuando el curso se atrasa o adelanta

El cronograma conserva la planeación; el estado comunica la realidad operativa.

- Si solo cambia dónde quedó la clase, actualiza `estado.toml` y la bitácora.
- Si cambia la planeación futura de manera efectiva, modifica `contenidos.toml`.
- Si cambia una fecha o modalidad, modifica `calendario.toml`.
- No alteres semanas pasadas únicamente para hacer parecer que el desarrollo coincidió con el plan.

## Cuando cambian las lecturas

1. Añade o corrige la entrada en `bibliografia/referencias.bib`.
2. Usa exactamente su clave en `cronograma/contenidos.toml`.
3. Ejecuta `python scripts/cronograma.py` para validar rápidamente.
4. Ejecuta `python scripts/build.py` para reconstruir todos los documentos.

El archivo `.bib` es la fuente bibliográfica; el TOML decide en qué semana aparece cada lectura.

## Actividades y materiales

Las fuentes reutilizables se organizan por contenido estable:

- `actividades/`: talleres, controles, seminarios y guías evaluativas reutilizables;
- `materiales/`: handouts, presentaciones, hojas de estudio, ejemplos o datos organizados por tema.

Los datos variables —fecha, grupo, plazo y enlace de entrega— no se incrustan en la fuente general. Se incorporarán en la configuración de la edición cuando exista el primer caso real.

Las entregas estudiantiles y el seguimiento académico permanecen en `Teaching/Private/` y en las áreas privadas de Drive, nunca en Git.

## Compilar

Flujo normal:

```bash
python scripts/build.py
```

Validación rápida del cronograma:

```bash
python scripts/cronograma.py
```

Si los auxiliares de LaTeX parecen obsoletos:

```bash
python scripts/build.py --clean
python scripts/build.py
```

`--clean` solo limpia `build/`; no toca las fuentes ni `dist/`.

## Publicar en Drive

Primero simula:

```bash
python scripts/publicar.py
```

Después publica:

```bash
python scripts/publicar.py --apply
```

Para hacer que una categoría coincida exactamente con la lista autorizada, archivando los sobrantes:

```bash
python scripts/publicar.py --clean
python scripts/publicar.py --clean --apply
```

La limpieza real mueve sobrantes a `09_Archivo`; no los destruye.

## Registrar el trabajo en Git

```bash
git status
git diff
git add .
git diff --cached
git diff --cached --stat
git commit -m "describe el cambio en minúscula"
git push
```

Antes de `git add .`, comprueba que no aparezcan listas, notas, entregas, credenciales ni archivos descargados accidentalmente.

## Rutina semanal recomendada

### Antes de clase

- actualizar estado;
- confirmar materiales y lecturas;
- compilar;
- revisar el correo generado;
- publicar si cambió un documento estudiantil.

### Después de clase

- actualizar bitácora;
- registrar pendientes;
- ajustar el estado de la próxima sesión;
- hacer commit y push de un cambio coherente.

## Qué es automático

- cálculo de fechas y sesiones desde `calendario.toml`;
- validación del cronograma y las claves BibTeX;
- generación de la tabla del cronograma;
- generación del estado y del borrador de correo;
- compilación de los tres PDF;
- copia conjunta de PDF válidos a `dist/`;
- simulación y publicación controlada en Drive.

## Qué sigue siendo decisión docente

- contenido del programa;
- secuencia académica del cronograma;
- selección de lecturas;
- descripción del estado real;
- preparación y avisos;
- diseño de actividades y materiales;
- notas de la bitácora.

## Cierre rápido de una jornada

```bash
python scripts/build.py
git status
git diff
git add .
git diff --cached --stat
git commit -m "actualiza operación del curso"
git push
```

Publica en Drive únicamente cuando haya cambiado un entregable que el estudiantado deba recibir.
