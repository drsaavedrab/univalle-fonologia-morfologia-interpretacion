
# Edición activa

Esta carpeta representa una edición concreta del curso.

Al crear un curso o periodo nuevo, `AAAA-P` debe reemplazarse por un identificador como:

```text
2026-2
2027-1
```

## Contenido

- `semestre.tex`: periodo, grupo, salón y horario.
- `planificacion.md`: estado y pendientes de la edición.
- `cronograma/contenido.tex`: cronograma específico.
- `publicacion.json`: categorías y destinos de Google Drive.

## Publicación

La simulación es el comportamiento predeterminado:

```bash
python scripts/publicar.py
```

La publicación real requiere:

```bash
python scripts/publicar.py --apply
```

Puede seleccionarse una categoría:

```bash
python scripts/publicar.py --only documentos_generales
```

## Contenido opcional

Solo cuando exista un caso real podrán crearse:

- `actividades/`: datos variables de actividades utilizadas;
- `materiales/`: contenidos exclusivos de la edición.

Las fuentes reutilizables permanecen en los bancos generales del curso.

## Información privada

Esta carpeta no debe contener listas estudiantiles, correos, calificaciones, entregas ni credenciales.