# Manual 3 — Operación cotidiana de un curso en marcha

Esta guía es para el uso semanal del repositorio una vez iniciado el periodo. El ejemplo práctico es MSE-II, pero el flujo sirve para cualquier curso creado con esta plantilla.

## Regla principal

Edita fuentes, genera salidas y publica entregables. Nunca edites directamente `build/`, `dist/*.pdf` ni archivos que ya estén en Drive.

## El flujo de Git que acompaña el trabajo

Git separa cuatro estados:

```text
archivos de trabajo → área de preparación → commit local → remoto en GitHub
      git diff             git add          git commit       git push
```

- Los **archivos de trabajo** son lo que estás editando en el computador.
- El **área de preparación** reúne deliberadamente los cambios del próximo commit.
- Un **commit local** es una instantánea recuperable con una explicación.
- El **remoto** es la copia compartida o de respaldo en GitHub.

Guardar un archivo en VS Code no equivale a hacer `git add`; hacer `git add` no equivale a crear un commit; y crear un commit no equivale a publicarlo.

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

Los DOCX reutilizables se versionan como fuentes, aunque Git no pueda mostrar diferencias internas línea por línea. Los PDF derivados no se versionan.

La selección semestral se declara en `ediciones/<periodo>/publicacion.json`. Por ejemplo:

```json
{
  "nombre": "materiales_semana_01",
  "origen": "dist/materiales/semana-01",
  "destino": "Lectures/INSTITUCION/CURSO/PERIODO/03_Materiales/Semana 01",
  "archivos": [
    "introduccion-a-la-gramatica.pdf"
  ],
  "conversiones": [
    {
      "fuente": "materiales/introduccion-a-la-gramatica/handout-estudiantes.docx",
      "salida": "introduccion-a-la-gramatica.pdf"
    }
  ]
}
```

`fuente` parte de la raíz del repositorio. `salida` es relativa a `origen` y debe aparecer también en `archivos`. Así una sola entrada decide qué fuente se usa, cómo se genera y dónde se publica durante el periodo.

Preparación sin acceder a Drive:

```bash
python scripts/materiales.py --only materiales_semana_01
```

Simulación completa de esa categoría:

```bash
python scripts/publicar.py --only materiales_semana_01
```

La simulación genera el PDF local si hace falta. Solo `--apply` lo sube.

Las entregas estudiantiles y el seguimiento académico permanecen fuera de Git y en las áreas privadas correspondientes.

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
git status
git diff --cached
git diff --cached --stat
git commit -m "describe el cambio en minúscula"
git push
```

Antes de `git add .`, comprueba que no aparezcan listas, notas, entregas, credenciales ni archivos descargados accidentalmente.

### Lectura paso a paso

1. `git status` clasifica archivos modificados, eliminados, nuevos, preparados y no preparados. Es el primer control de alcance.
2. `git diff` muestra los cambios de contenido que aún no han pasado por `git add`.
3. `git add .` prepara todo lo que cuelga de la carpeta actual. Úsalo desde la raíz y solo después de revisar `status`. Si el trabajo es muy concreto, es más seguro indicar las rutas:

   ```bash
   git add ediciones/2026-2/operacion/estado.toml ediciones/2026-2/bitacora.md
   ```

4. El segundo `git status` permite comprobar que no preparaste algo ajeno al objetivo.
5. `git diff --cached` —equivalente a `git diff --staged`— muestra el contenido preparado; `--stat` muestra solo cantidades y nombres.
6. `git commit -m "..."` crea el registro local. El mensaje debe describir el resultado, no el acto mecánico de editar.
7. `git push` envía a GitHub los commits que tu rama local tiene por delante de `origin/main`.

### Si preparaste un archivo por error

```bash
git restore --staged ruta/del/archivo
```

Esto lo retira del área de preparación, pero conserva tus cambios en el archivo. No uses `git restore ruta/del/archivo` salvo que realmente quieras descartar cambios no confirmados.

### Qué debe contener un commit cotidiano

Un commit debe representar una unidad comprensible. Ejemplos:

- `actualiza estado después de la sesión 3`;
- `reprograma sesiones por festivo`;
- `añade lecturas sobre subordinación`.

Si modificaste simultáneamente el estado operativo y una sección estable del programa, puedes crear dos commits añadiendo primero las rutas de un grupo y luego las del otro.

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
git diff --cached --check
git diff --cached --stat
git commit -m "actualiza operación del curso"
git push
```

`git diff --cached --check` no muestra normalmente ninguna salida: busca problemas como espacios finales o marcadores de conflicto dentro de lo preparado. Que termine en silencio significa que no encontró esos problemas.

Publica en Drive únicamente cuando haya cambiado un entregable que el estudiantado deba recibir.
