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

Comprueba dónde estás:

```bash
pwd
git status
```

## 2. Crear la primera edición

Sustituye `2026-2` por el periodo real:

```bash
git mv ediciones/AAAA-P ediciones/2026-2
```

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
- `ediciones/2026-2/cronograma/calendario.toml`: fechas, días de clase y excepciones;
- `ediciones/2026-2/cronograma/contenidos.toml`: semanas, sesiones, temas, lecturas y actividades;
- `ediciones/2026-2/operacion/estado.toml`: estado inicial, próxima sesión y aviso posterior a clase;
- `ediciones/2026-2/operacion/bienvenida.toml`: contenido del correo inicial;
- `ediciones/2026-2/publicacion.json`: rutas del curso en Drive;
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
git add .
git diff --cached --stat
git commit -m "configura curso y primera edición"
git push -u origin main
```

## Comprobación final

- [ ] No quedan marcadores involuntarios.
- [ ] Los tres PDF compilan.
- [ ] El correo generado usa el nombre del curso y del docente.
- [ ] La simulación de Drive apunta al destino correcto.
- [ ] No hay listas, notas, entregas ni credenciales en Git.
- [ ] El repositorio remoto pertenece únicamente a este curso.
