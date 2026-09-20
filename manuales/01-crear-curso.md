# Manual 1 — Crear un curso desde la plantilla

Esta guía se usa una sola vez por curso académico estable. No se usa para abrir un semestre nuevo de un curso existente.

## Resultado esperado

Al terminar habrá un repositorio independiente dentro de `Teaching/Lectures/<INSTITUCIÓN>/`, con su propio historial de Git, configuración, programa, bibliografía y primera edición.

## 1. Crear el repositorio local

Desde la carpeta de la institución, en Git Bash:

```bash
cd ~/Documents/Teaching/Lectures/INSTITUCION
git clone --no-local ../../Templates/course-repo nombre-del-curso
cd nombre-del-curso
git remote remove origin
```

`--no-local` crea una copia Git independiente. Al retirar `origin`, el curso nuevo deja de apuntar a la plantilla.

### Qué acaba de ocurrir en Git

- `git clone --no-local ... nombre-del-curso` copia los archivos **y el historial** de la plantilla. El curso nace con una base conocida, pero su trabajo posterior será independiente.
- `cd nombre-del-curso` entra en el nuevo repositorio. Git solo interpreta los comandos respecto del repositorio en el que estás situado.
- `git remote remove origin` elimina la conexión con el repositorio remoto de la plantilla. No borra archivos ni commits: únicamente evita que un `push` accidental modifique la plantilla.

Comprueba dónde estás:

```bash
pwd
git status
git remote -v
```

`pwd` confirma la ubicación; `git status` compara los archivos actuales con el último commit; `git remote -v` debe quedar sin resultados hasta que conectes el repositorio propio del curso.

## 2. Crear la primera edición

Sustituye `2026-2` por el periodo real:

```bash
git mv ediciones/AAAA-P ediciones/2026-2
```

Se usa `git mv` porque la carpeta ya pertenece al historial de la plantilla. El comando mueve el contenido y deja preparado para Git que se trata de un cambio de nombre, no de una eliminación accidental seguida de archivos inconexos.

Después cambia en `config/edicion-activa.tex`:

```latex
\newcommand{\edicionActiva}{2026-2}
```

Reemplaza también `AAAA-P` dentro de los archivos de la edición.

## 3. Configurar la identidad estable

Edita `config/curso.tex`. Aquí van los datos que describen el curso y normalmente sobreviven a varios periodos:

- institución, facultad y unidad académica;
- nombre y código del curso;
- plan de estudios, créditos y prerrequisitos;
- docente y correo;
- atención a estudiantes;
- ruta del logo y texto institucional del encabezado.

Guarda el logo en `recursos/identidad/`. Puedes conservar el nombre `logo-institucion.png` o ajustar `\rutaLogoInstitucional`.

## 4. Configurar la primera edición

Edita únicamente los datos variables del periodo:

- `ediciones/2026-2/semestre.tex`: periodo, grupo, salón y horario;
- `ediciones/2026-2/cronograma/calendario.toml`: fechas, días de clase, excepciones y visibilidad de la columna «Sesión»;
- `ediciones/2026-2/cronograma/contenidos.toml`: semanas, sesiones, temas, lecturas y actividades;
- `ediciones/2026-2/operacion/estado.toml`: estado inicial, próxima sesión y aviso posterior a clase;
- `ediciones/2026-2/operacion/bienvenida.toml`: contenido del correo inicial;
- `ediciones/2026-2/publicacion.json`: rutas del curso en Drive y selección semestral de materiales DOCX→PDF;
- `ediciones/2026-2/bitacora.md`: pendientes y notas de trabajo.

## 5. Incorporar el programa y la bibliografía

El programa estable se edita en `programa/secciones/`. Conserva un archivo por sección.

La bibliografía se administra en `bibliografia/referencias.bib`. Cada lectura del cronograma usa una `clave` existente en ese archivo. Primero crea o confirma la entrada BibTeX; después usa su clave en `contenidos.toml`.

Elimina `referencia-pendiente` cuando ya exista bibliografía real y actualiza la fila de ejemplo que la utiliza.

## 6. Revisar marcadores pendientes

Desde la raíz:

```bash
grep -RInE "AAAA-P|INSTITUCIÓN|NOMBRE DEL CURSO|NOMBRE_CURSO|GRUPO|SALÓN|HORARIO|REFERENCIA PENDIENTE" . --exclude-dir=.git --exclude-dir=build --exclude-dir=dist
```

Cada coincidencia debe ser intencional o quedar corregida antes de publicar.

Este comando no modifica nada: `grep` solo busca texto. Tampoco es un comando de Git, aunque excluimos `.git` para no revisar el historial interno.

## 7. Generar y revisar

```bash
python scripts/build.py
```

Revisa:

- `dist/programa.pdf`;
- `dist/cronograma.pdf`;
- `dist/estado-del-curso.pdf`;
- `build/correos/bienvenida.txt`;
- `build/correos/aviso-posclase.txt`.

`build/` es automático. `dist/` contiene entregables y tampoco se edita manualmente.

## 8. Configurar Drive

Ejecuta primero una simulación:

```bash
python scripts/publicar.py
```

Solo cuando las rutas y la lista de archivos sean correctas:

```bash
python scripts/publicar.py --apply
```

Las credenciales de rclone nunca se guardan en el repositorio.

## 9. Crear el repositorio remoto

Crea en GitHub un repositorio vacío con el nombre del curso. Después:

```bash
git remote add origin URL-DEL-REPOSITORIO
git remote -v
git status
git diff
git add .
git status
git diff --cached
git diff --cached --stat
git commit -m "configura curso y primera edición"
git push -u origin main
```

### Qué hace Git en esta secuencia

1. `git remote add origin ...` conecta el repositorio local con el repositorio vacío de GitHub. `origin` es el nombre convencional de esa conexión.
2. `git remote -v` permite verificar las direcciones antes de publicar nada.
3. `git status` muestra archivos modificados, nuevos y eliminados. Aquí sirve para detectar archivos privados o generados que no deban entrar en Git.
4. `git diff` enseña el contenido modificado que todavía no se ha preparado. Los archivos completamente nuevos aparecen en `status`, pero su contenido aún no aparece en este diff.
5. `git add .` lleva los cambios revisados al **área de preparación** o *staging area*. Todavía no crea un commit.
6. El segundo `git status` confirma exactamente qué quedó preparado.
7. `git diff --cached` muestra el contenido que formará el commit; `--stat` ofrece el resumen por archivo. `--staged` significa lo mismo que `--cached`.
8. `git commit -m "..."` registra una instantánea local con un mensaje que explica la unidad de cambio.
9. `git push -u origin main` publica la rama `main` por primera vez y deja configurada su relación con `origin/main`. En adelante bastará con `git push`.

El orden importa: primero se inspecciona, después se prepara, luego se vuelve a inspeccionar y solo entonces se registra y publica.

## Comprobación final

- [ ] No quedan marcadores involuntarios.
- [ ] Los tres PDF compilan.
- [ ] El correo generado usa el nombre del curso y del docente.
- [ ] La simulación de Drive apunta al destino correcto.
- [ ] No hay listas, notas, entregas ni credenciales en Git.
- [ ] El repositorio remoto pertenece únicamente a este curso.
