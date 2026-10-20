# Reestructuración local — 2026-10-20

Migración del repositorio en la carpeta de trabajo existente. No se conectó al vehículo ni se actualizaron sus parámetros, firmware o servicios. La última observación física sigue siendo la del 2026-10-19.

## Preservación

Se creó el respaldo privado hermano `kame-respaldo-20261020-122102/original/`: **116 archivos, 805.129.853 bytes**, cotejados individualmente mediante SHA-256. El manifiesto de ese respaldo está en su `manifest.json`. Su ACL y la de `local/` permiten al usuario actual y SYSTEM acceder; no se publica el respaldo.

`local/migracion.json` registra la ruta absoluta del respaldo y el destino de cada archivo original. Las credenciales se extrajeron a `local/credenciales.md` antes de crear el primer commit saneado. Los archivos crudos y recursos pesados se conservan bajo `local/`; el [inventario](recursos.json) contiene sus hashes sin incluir credenciales.

## Cambio

Se agruparon los tres componentes existentes en software, SITL en simulación y los borradores en misiones. La raíz conserva un README y un AGENTS; el plan tiene cinco fases y el estado sigue en fase 1. El antiguo contexto y la propuesta extensa se consolidaron y sus originales se archivaron en `local/archivo/` y en Git saneado.

Se actualizaron enlaces y rutas relativas; el generador admite `--output-dir`. SITL utiliza los binarios locales y un directorio de estado nuevo, conserva su configuración y `--wipe`, y limpia sus dos procesos al terminar. Los destinos de instalación de la Raspberry no cambian.

## Verificaciones

| Comprobación | Resultado |
| --- | --- |
| Preservación | Los 116 originales tienen destino y respaldo cuyo SHA-256 coincide. 102 archivos siguen idénticos en su destino; 14 documentos/scripts se editaron y conservan el original verificado en el respaldo. |
| ACL privada | Se verificaron 254 rutas del respaldo y recursos locales: acceso del usuario actual y SYSTEM. |
| Comprobaciones portátiles | Python 3.12.10 y Node.js 24.15.0 en Windows: 52 archivos, sintaxis Python/JavaScript, scripts HTML, configuración JSON, 101 enlaces/anclas Markdown y patrones de secretos, correctos. |
| Misiones | Los dos borradores regenerados en un destino temporal desde otro directorio coinciden con los originales, normalizando finales de línea al leer. |
| Visor | Página, API, eventos SSE y cambio Wi-Fi/Ethernet correctos usando un preload que reemplaza todas las consultas fetch del visor por datos simulados. No se consultó BlueOS. |
| SITL | Ubuntu 22.04 de WSL, x86_64: arranque con los defaults existentes y heartbeat de contador 3 a 6, desarmado. SIGTERM al lanzador cerró sus procesos y liberó HTTP 8088/UDP 14550. |
| YAML | Workflow, formulario de tarea y configuración MediaMTX analizados localmente con PyYAML. El workflow todavía no se ha ejecutado en GitHub. |
| Clon limpio | Se clonó Git en `local/verificacion/checkout/`, sin credenciales, binarios ni modelos. Las comprobaciones portátiles completas también pasaron allí. |
| Git | Base saneada `586435a`; migración `59b7323`; comprobaciones y plantillas `698a005`. La entrega se integra en `main` mediante avance rápido; no se configura remoto. |

El ensayo SITL detectó que este binario MAVLink2REST representa bitflags mediante nombres; el comprobador acepta tanto nombres como valores numéricos. También distingue los sockets TIME_WAIT de un puerto ocupado por un listener. Estas adaptaciones corresponden al comprobador local, no a cambios del vehículo ni del visor.

Para repetir desde la raíz: `python .github/checks/check_repository.py`; en Linux/WSL con recursos locales: `python3 .github/checks/check_sitl.py`. El registro del ensayo correcto está en `local/registros/sitl/check-20261020-103045-903997Z.log`. La revisión de secretos cubre patrones y, cuando existe el archivo privado, sus valores conocidos; sigue siendo necesaria la revisión del contenido antes de publicar.

## Recuperación y límites

Para recuperar la distribución original, preservar antes cualquier cambio posterior y copiar el respaldo verificado a otra carpeta. Para revisar el código anterior, utilizar el commit inicial saneado; ese commit no incluye recursos ignorados. Los recursos pueden recuperarse del respaldo privado y cotejarse por hash.

La procedencia de descarga/build de varios binarios y modelos sigue pendiente. Un clon limpio permite comprobar el código; no incluye los recursos privados ni certifica la instalación de YOLO o la calibración del barco. La publicación en GitHub y la licencia están pendientes.
