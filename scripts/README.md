# Scripts

## Flujo principal

`python scripts/build.py` valida la edición activa, genera cronograma, estado y correos, compila los tres documentos públicos y actualiza conjuntamente `dist/`. No modifica Google Drive.

Las salidas operativas son:

- `build/correos/bienvenida.txt`;
- `build/correos/aviso-posclase.txt`.

## Módulos

### `build.py`

Orquesta el flujo completo. `python scripts/build.py --clean` elimina únicamente auxiliares de `build/`, conserva `.gitkeep` y no modifica `dist/`.

### `cronograma.py`

Valida calendario, contenidos y claves BibTeX y genera `build/cronograma-contenido.tex`. Normalmente lo llama `build.py`.

```bash
python scripts/cronograma.py
python scripts/cronograma.py --clean
```

### `estado.py`

Combina `operacion/estado.toml` con el calendario y genera `build/estado-contenido.tex`. No redacta ni envía correos.

### `correos.py`

Combina las plantillas de `correos/plantillas/` con los TOML de la edición y genera borradores de texto plano.

```bash
python scripts/correos.py
python scripts/correos.py --only bienvenida
python scripts/correos.py --only aviso-posclase
```

La bienvenida usa `operacion/bienvenida.toml`. El aviso posterior a clase usa `operacion/estado.toml` y calcula la próxima sesión desde el calendario. Ningún comando envía mensajes.

### `publicar.py`

`python scripts/publicar.py` simula la publicación. La modificación real de Drive exige `--apply`. Puede limitarse con `--only documentos_generales`.

```bash
python scripts/publicar.py
python scripts/publicar.py --apply
python scripts/publicar.py --clean
python scripts/publicar.py --clean --apply
```

Con `--clean --apply`, los sobrantes se mueven a la ruta `archivo` de `publicacion.json`, dentro de `09_Archivo`, y se aplica un máximo de veinte retiros.

## Qué limpia cada opción

| Comando | Modifica | No modifica |
|---|---|---|
| `build.py --clean` | auxiliares y correos generados de `build/` | fuentes, `dist/`, Git, Drive |
| `cronograma.py --clean` | fragmento generado del cronograma | TOML, `.bib`, PDF, Drive |
| `publicar.py --clean` | nada: solo simula | todo |
| `publicar.py --clean --apply` | destino administrado; archiva sobrantes | repositorio local y otras carpetas de Drive |

## Seguridad

Las credenciales de rclone nunca se guardan en Git. Solo se publican archivos enumerados en `publicacion.json`. Los borradores deben revisarse y copiarse manualmente al cliente de correo.
