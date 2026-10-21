# BlueOS: adaptación PWM omitida por el bus I²C de la cámara — 2026-10-20

**ID:** `F1-BLUEOS-I2C-20261020-224648`. Inspección de solo lectura el 2026-10-20, 22:46–22:48 CEST (Europe/Madrid), solicitada por el usuario: «hazlo ya», después de concretar la comprobación de dispositivos, proceso y registros del parche. Objetivo: determinar si la adaptación oficial de BlueOS entre I²C 4 y 3 existe, si está actuando y qué ocupa el bus 4.

## Dictamen

**La adaptación oficial está instalada y habilitada, pero no está redirigiendo el acceso PWM.** `/dev/i2c-4` es un dispositivo de caracteres real, número 89:4, utilizado por el sensor CSI `imx290 4-001a` (nombre interno documentado de la IMX462). ArduPilot abre ese mismo dispositivo 89:4, mientras el PWM fue identificado previamente en el bus físico 3. No hay enlace simbólico entre los nombres 4 y 3 en el anfitrión, en BlueOS ni en el entorno del proceso.

La función oficial devuelve sin crear el enlace cuando `/dev/i2c-4` ya existe. La combinación de su código instalado, las comprobaciones actuales y el registro de ejecución del parche identifica el conflicto presente. **No demuestra que una actualización concreta lo introdujera ni que faltara configuración inicial.** Los registros conservados acreditan que el enlace se creó correctamente anteriormente, también con BlueOS 1.4.3.

## Entorno, autorización y método

Raspberry Pi 5, kernel `6.6.31+rpt-rpi-2712`, BlueOS `1.4.3-0-gc38aa1ee`, Navigator64 y ejecutable original ArduRover 4.7.2. Acceso HTTP/MAVLink2REST y SSH con autenticación por contraseña, sin claves ni agente. Credenciales utilizadas solo en memoria, excluidas de comandos y evidencias. Python 3.12 y biblioteca Paramiko ya disponible en el PC; no se instaló software en el barco.

Rama `codex/local-git-authorization-rules`, commit `621a432c45de30500211aa906de82ccbda6cf549`; cambios preexistentes registrados en `session.json` y preservados. Se consultaron metadatos de `/dev`, `/sys` y `/proc`, código y registros instalados, configuración de arranque y copias antiguas. No se abrió ningún bus para transacciones I²C, no se ejecutó la función del parche y no se cambiaron archivos, firmware, servicios, GPIO, parámetros ni señales PWM. No hubo armado, giro o reinicios.

## Lecturas directas

| Comprobación | Resultado |
| --- | --- |
| Heartbeat inicial | Tres mensajes con contadores 6880, 6883 y 6885, fecha creciente y desarmado, entre las 22:46:48 y 22:46:53 CEST. |
| Heartbeat final | Contadores 6957 y 6960, últimas actualizaciones 22:48:05 y 22:48:08 CEST; `base_mode.bits=9`, desarmado. |
| Proceso | Un ejecutable activo Navigator64, PID 473050, SHA-256 `e0cede800da4bd895ec3d60f2d4ea68879e16f6da6998716440f8dded5ed736e`, coincidente con el original oficial identificado en la [auditoría del firmware](2026-10-20-firmware-pi5.md). |
| Dispositivos abiertos | Descriptor 5 hacia `/dev/i2c-4`, número 89:4; descriptor 9 hacia `/dev/i2c-1`, número 89:1. No se observó descriptor del bus 3. |
| Dispositivos del anfitrión, contenedor y proceso | `/dev/i2c-3` es dispositivo de caracteres 89:3 y `/dev/i2c-4` es dispositivo de caracteres 89:4. Ninguno es enlace simbólico. Se contrastó también `/proc/473050/root/dev/`. |
| Asignación activa | Bus 3, controlador `1f0007c000.i2c`, GPIO6/GPIO7. Bus 4, controlador `1f00080000.i2c`, GPIO40/GPIO41. Referencias `pinctrl-0` resueltas en el árbol activo. |
| Cliente del bus 4 | `4-001a`, nombre `imx290lqr`, controlador del kernel `imx290`, nodo `i2c@80000/imx290@1a`, compatible `sony,imx290lqr`, estado `okay`. El subdispositivo de vídeo `imx290 4-001a` resuelve al mismo cliente. |
| Configuración de cámara | `/boot/firmware/config.txt` contiene `dtoverlay=imx462`. Las copias antiguas incluyen variantes con y sin este overlay y una variante `imx462,cam0`. No se restauró ninguna. |
| Parche instalado | `/home/pi/tools/blueos_startup_update/blueos_startup_update.py`, SHA-256 original `7ed1981be35ed4d0803ff12bf966fae06017fe44839fb10e553c3390c86d869a`, idéntico al archivo oficial 1.4.3 descargado al PC. |
| Supresión y protección de arranque | `BLUEOS_DISABLE_PATCHES` no aparece en el entorno consultado del contenedor; el marcador `/root/.config/.boot_loop_detector` no existe. Los registros confirman `i2c4 (enabled)` y la entrada en su función. |

La identificación IMX462/imx290 ya estaba documentada en el [registro de cámara](2026-10-09-video.md). Aquí se confirma además su ubicación actual en el bus físico 4; no se evaluó la reproducción de vídeo ni la generación PWM.

## Por qué no se crea el enlace

El [código oficial 1.4.3](https://github.com/bluerobotics/BlueOS/blob/1.4.3/core/tools/blueos_startup_update/blueos_startup_update.py#L272-L282) conserva este orden: si existe `/dev/i2c-4`, termina; si falta `/dev/i2c-3`, termina; en otro caso solicita crear el enlace 4→3. El parche está registrado para Pi 5 y el código instalado coincide con el oficial por hash calculado antes de sanear la copia textual de evidencia.

**Hecho observado:** el nombre 4 corresponde ahora a un controlador físico con un sensor de cámara. **Deducción del código y ese estado:** se cumple la condición que omite la creación del enlace. No se volvió a ejecutar el parche para provocar o trazar esa decisión. La ausencia del enlace no es una diferencia entre los espacios de dispositivos del anfitrión y el contenedor: ambos exponen el mismo dispositivo 89:4, que también abre ArduPilot.

El conflicto concuerda con la [incidencia oficial #3984](https://github.com/bluerobotics/BlueOS/issues/3984), que describe I²C 4 en CAM/DISP1, GPIO40/41, y el enlace que BlueOS utiliza para Navigator. Reemplazar globalmente ese nodo para forzar el enlace afectaría al acceso de la cámara; no se hizo esa operación.

## Qué dicen los registros antiguos

Se examinaron extractos dirigidos de 52 archivos archivados de `blueos_startup_update`: los 52 registran el parche `i2c4` habilitado y la entrada en su función; 27 registran la orden de creación del enlace con código de retorno 0. Hay creaciones correctas bajo BlueOS 1.4.3, incluidas entradas de octubre. Por tanto, el mecanismo oficial sí se llegó a aplicar con esa misma versión.

Los registros con marcas internas del 6 de octubre contienen creación correcta; el 7 aparecen tanto creaciones como invocaciones sin creación, y las entradas posteriores consultadas no muestran la orden de creación. Las copias de arranque nombradas el 7 de octubre conservan cambios de configuración de cámara. Esto refuerza la relación temporal con su preparación, **sin identificar por sí solo el primer fallo**: cuando un enlace correcto ya existe, la función también termina sin volver a crearlo. Los logs no registran en cada invocación el tipo del nodo existente ni prueban giro físico de los motores.

Hay marcas internas de reloj anteriores a las fechas de publicación de las versiones declaradas y los nombres de archivos corresponden a archivado/rotación. Se conservan ambas referencias; no se usa un nombre o `mtime` aislado para atribuir la avería a una actualización o a una persona.

## Estado final y siguiente paso

**En el vehículo:** firmware original funcionando y heartbeat fresco desarmado en la lectura final; adaptación sin enlace, cámara en bus 4. Esta inspección no tiene cambios operativos que revertir. **En repositorio:** informe, índice y síntesis de estado. La comprobación del mecanismo de BlueOS está completada; no acredita una reparación ni una prueba de propulsión.

La solución debe preservar el acceso de la cámara al bus 4 y dirigir el PWM al bus 3. La selección del bus en el controlador de ArduPilot sigue siendo una alternativa compatible con ese objetivo; restaurar indiscriminadamente el enlace global de BlueOS no lo es mientras la cámara utilice el nodo real 4. Cambiar firmware, asignación de cámara o exponer dispositivos de otro modo requiere una intervención específica con respaldo, autorización y verificación de PWM/vídeo. No se inició esa intervención aquí.

Evidencias privadas bajo `local/registros/F1-BLUEOS-I2C-20261020-224648/`: sesión Git, comandos/horas/códigos de retorno, heartbeat, dispositivos y descriptores con números mayor/menor, fuente instalada saneada y sus hashes originales, comparación con fuente oficial, extractos y hashes de logs, resumen histórico, configuración de arranque seleccionada, nodos de cámara, `inspection-result.json` y `SHA256.json`. Los logs persistidos son extractos seleccionados, no copias completas; los hashes de contenido original se calcularon antes de filtrar.

Comprobaciones locales: `python .github/checks/check_repository.py` con Python 3.12 pasó sobre 71 archivos y 197 enlaces/anclas, incluyendo sintaxis/configuración, patrones de secretos, equivalencia de misiones y visor. `git diff --check` de los documentos versionados afectados no señaló errores. Estas comprobaciones no validan la señal eléctrica, la cámara en reproducción ni una reparación del vehículo.
