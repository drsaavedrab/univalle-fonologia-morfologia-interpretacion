# Correos

Esta carpeta contiene plantillas versionadas de comunicaciones docentes. No contiene mensajes enviados ni datos de estudiantes.

## Plantillas actuales

- `plantillas/bienvenida.txt`: mensaje inicial de cada periodo.
- `plantillas/aviso-posclase.txt`: actualización posterior a una clase y preparación para la siguiente.

Los textos concretos se generan en `build/correos/` y están excluidos de Git. La bienvenida toma sus datos de `ediciones/<periodo>/operacion/bienvenida.toml`; el aviso posterior a clase toma los suyos de `estado.toml` y del calendario.

## Generación

```bash
python scripts/correos.py
python scripts/correos.py --only bienvenida
python scripts/correos.py --only aviso-posclase
```

El flujo completo `python scripts/build.py` genera siempre ambos borradores.

## Qué se modifica

- Cambia la plantilla solo cuando deba cambiar la estructura común a todos los periodos.
- Cambia los TOML cuando varíe el contenido de una edición.
- Copia el borrador desde `build/correos/` a tu cliente de correo y revísalo antes de enviarlo.

El sistema no envía mensajes automáticamente.
