
# Scripts

Esta carpeta contiene las herramientas de automatización del repositorio.

## `build.py`

Compila los documentos principales:

```bash
python scripts/build.py
```

El proceso:

1. compila el programa y el cronograma;
2. almacena los archivos técnicos en `build/`;
3. comprueba que ambas compilaciones terminen correctamente;
4. actualiza los PDF de `dist/`.

Si una compilación falla, `dist/` no debe quedar parcialmente actualizado.

## `publicar.py`

Publica los archivos autorizados de la edición activa mediante rclone.

Simulación:

```bash
python scripts/publicar.py
```

Publicación real:

```bash
python scripts/publicar.py --apply
```

Selección de una categoría:

```bash
python scripts/publicar.py --only documentos_generales
```

Publicación real de una categoría:

```bash
python scripts/publicar.py --only documentos_generales --apply
```

El comportamiento predeterminado es siempre una simulación. Esto permite revisar el destino y los archivos antes de modificar Google Drive.

## Configuración

`publicar.py` lee:

```text
config/edicion-activa.tex
```

Después carga:

```text
ediciones/<edicion-activa>/publicacion.json
```

Las credenciales de Google Drive pertenecen a la configuración local de rclone y nunca deben añadirse a Git.

## Principios de seguridad

Los scripts no deben:

- publicar archivos no enumerados;
- almacenar credenciales;
- publicar información privada;
- eliminar automáticamente contenido de Google Drive.