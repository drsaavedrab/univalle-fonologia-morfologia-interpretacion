# Manual 2 — Abrir un periodo nuevo en el mismo curso

Esta guía se usa cuando el curso académico es el mismo, pero comienza una nueva ejecución semestral. No se crea otro repositorio.

## Principio

El núcleo estable permanece en `programa/`, `bibliografia/`, `actividades/`, `materiales/`, `recursos/` y `config/curso.tex`. La información del nuevo periodo vive en una carpeta nueva dentro de `ediciones/`.

## 1. Cerrar y conservar el periodo anterior

Antes de abrir el siguiente:

- completa el balance final de `ediciones/<periodo-anterior>/bitacora.md`;
- confirma que los PDF finales estén publicados;
- ejecuta `git status` y deja el repositorio limpio;
- no renombres ni reemplaces la carpeta anterior.

## 2. Crear la nueva edición

Como punto de partida, copia la edición anterior completa y luego limpia sus datos operativos. En Git Bash:

```bash
cp -R ediciones/2026-2 ediciones/2027-1
```

La copia aprovecha la estructura ya validada, pero todavía no está lista para usarse.

## 3. Actualizar los archivos del periodo

En `ediciones/2027-1/`:

1. `semestre.tex`: cambia periodo, grupo, salón y horario.
2. `cronograma/calendario.toml`: cambia inicio, fin, días ordinarios y excepciones.
3. `cronograma/contenidos.toml`: revisa cada semana y sesión; conserva contenidos útiles, pero no supongas que el calendario será idéntico.
4. `operacion/estado.toml`: vuelve al estado de inicio y borra avisos antiguos.
5. `operacion/bienvenida.toml`: actualiza el mensaje inicial, la preparación y el enlace compartido.
6. `publicacion.json`: sustituye el periodo y confirma la ruta en Drive.
7. `bitacora.md`: elimina el desarrollo anterior, conserva la estructura y escribe los pendientes iniciales.
8. `README.md`: actualiza el nombre del periodo cuando corresponda.

No copies listas estudiantiles, notas, entregas ni enlaces de formularios. Esos datos se crean para el periodo nuevo fuera del repositorio o en su configuración privada.

## 4. Decidir qué cambios pertenecen al núcleo

Antes de editar el programa o los bancos generales, clasifica el cambio:

| Cambio | Ubicación |
|---|---|
| fecha, grupo, salón, horario | `ediciones/<periodo>/semestre.tex` |
| calendario, festivo o ausencia | `ediciones/<periodo>/cronograma/calendario.toml` |
| orden semestral de temas y lecturas | `ediciones/<periodo>/cronograma/contenidos.toml` |
| estado real y preparación próxima | `ediciones/<periodo>/operacion/estado.toml` |
| observación sobre esta ejecución | `ediciones/<periodo>/bitacora.md` |
| mejora estable del programa | `programa/secciones/` |
| referencia reutilizable | `bibliografia/referencias.bib` |
| actividad reutilizable | `actividades/` |
| material reutilizable por tema | `materiales/` |

## 5. Activar el nuevo periodo

Solo cuando su carpeta esté revisada, cambia `config/edicion-activa.tex`:

```latex
\newcommand{\edicionActiva}{2027-1}
```

Este es el interruptor central: programa, cronograma, estado y scripts usarán esa edición.

## 6. Validar y compilar

```bash
python scripts/build.py --clean
python scripts/build.py
```

Comprueba que:

- las fechas correspondan al nuevo calendario;
- todas las semanas y sesiones de `contenidos.toml` existan;
- las claves bibliográficas sean válidas;
- el estado identifique correctamente la sesión inicial;
- los tres PDF pertenezcan al nuevo periodo.

## 7. Simular la publicación

```bash
python scripts/publicar.py
```

Lee con cuidado edición activa, origen, destino y archivos. Después, si todo es correcto:

```bash
python scripts/publicar.py --apply
```

## 8. Registrar el cambio

```bash
git status
git diff
git add config/edicion-activa.tex ediciones/2027-1
git diff --cached --stat
git commit -m "abre edición 2027-1"
git push
```

Si además cambiaste componentes estables, es preferible registrarlos en un commit separado para que quede claro qué pertenece al curso y qué pertenece al periodo.

## Comprobación final

- [ ] La edición anterior permanece intacta.
- [ ] La edición activa apunta al nuevo periodo.
- [ ] No quedan fechas, rutas ni avisos heredados por accidente.
- [ ] Los tres documentos compilan.
- [ ] Drive se simuló antes de publicar.
- [ ] Los cambios estables y semestrales se distinguen en Git.
