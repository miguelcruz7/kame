# Reestructuración local — 2026-10-20

Migración del repositorio en la carpeta de trabajo existente. No se conectó al vehículo ni se actualizaron sus parámetros, firmware o servicios. La última observación física sigue siendo la del 2026-10-19.

## Preservación

Se creó el respaldo privado hermano `kame-respaldo-20261020-122102/original/`: **116 archivos, 805.129.853 bytes**, cotejados individualmente mediante SHA-256. El manifiesto de ese respaldo está en su `manifest.json`. Su ACL y la de `local/` permiten al usuario actual y SYSTEM acceder; no se publica el respaldo.

`local/migracion.json` registra la ruta absoluta del respaldo y el destino de cada archivo original. Las credenciales se extrajeron a `local/credenciales.md` antes de crear el primer commit saneado. Los archivos crudos y recursos pesados se conservan bajo `local/`; el [inventario](recursos.json) contiene sus hashes sin incluir credenciales.

## Cambio

Se agruparon los tres componentes existentes en software, SITL en simulación y los borradores en misiones. La raíz conserva un README y un AGENTS; el plan tiene cinco fases y el estado sigue en fase 1. El antiguo contexto y la propuesta extensa se consolidaron y sus originales se archivaron en `local/archivo/` y en Git saneado.

Se actualizaron enlaces y rutas relativas; el generador admite `--output-dir`. SITL utiliza los binarios locales y un directorio de estado nuevo, conserva su configuración y `--wipe`, y limpia sus dos procesos al terminar. Los destinos de instalación de la Raspberry no cambian.

## Verificaciones

En curso durante la migración. Esta sección se completará con los resultados obtenidos antes de cerrar la entrega.

## Recuperación y límites

Para recuperar la distribución original, preservar antes cualquier cambio posterior y copiar el respaldo verificado a otra carpeta. Para revisar el código anterior, utilizar el commit inicial saneado; ese commit no incluye recursos ignorados. Los recursos pueden recuperarse del respaldo privado y cotejarse por hash.

La procedencia de descarga/build de varios binarios y modelos sigue pendiente. Un clon limpio permite comprobar el código; no incluye los recursos privados ni certifica la instalación de YOLO o la calibración del barco. La publicación en GitHub y la licencia están pendientes.
