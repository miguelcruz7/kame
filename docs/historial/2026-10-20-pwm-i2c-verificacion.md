# Verificación I²C del PWM: inspección pendiente por ensayo concurrente — 2026-10-20

**ID:** `F1-PWM-I2C-20261020-215029`. Lecturas del 2026-10-20, 21:50:29–21:53:18 CEST (Europe/Madrid). Objetivo: repetir con evidencia fresca la comprobación del bus que usa el ArduPilot en ejecución frente al bus conectado al PCA9685 del Navigator. **Inspección incompleta: no se hicieron transacciones I²C porque no había heartbeat fresco ni un ejecutable activo del autopiloto.**

## Autorización, entorno y método

El usuario pidió implementar el plan de inspección de solo lectura y confirmó en esta conversación «Sí, ya están aislados» respecto de los ESC, sin especificar cuál de los dos métodos de aislamiento propuestos utilizó. Es una confirmación presencial comunicada; no hubo inspección visual independiente. Este encargo no autoriza arrancar o detener servicios, cambiar firmware, parámetros, GPIO o buses, ni generar PWM, armar o accionar motores.

Acceso por ZeroTier mediante HTTP/MAVLink2REST y SSH con contraseña, sin claves ni agente. Raspberry Pi 5 Model B Rev 1.1, `aarch64`, kernel `6.6.31+rpt-rpi-2712`, contenedor BlueOS `bluerobotics/blueos-core:1.4.3`. Herramienta local con Python 3.12 y Paramiko ya disponible; no se instaló software en el vehículo. Rama `codex/local-git-authorization-rules`, commit `621a432c45de30500211aa906de82ccbda6cf549`; los cambios locales preexistentes están registrados en `session.json` y se preservaron.

Las consultas al chip se condicionaron a heartbeat fresco y desarmado, proceso único y aislamiento confirmado. Al fallar la condición de frescura, solo se continuó con metadatos del SO, archivos y API para identificar el bloqueo. La selección de registro y lectura I²C prevista no llegó a ejecutarse.

## Resultados directos y límites

| Comprobación | Resultado y alcance |
| --- | --- |
| Heartbeat remoto | Primera lectura a las 21:50:30 CEST con contador 3898, última actualización 21:49:44,232 CEST. Tres lecturas adicionales separadas por dos segundos y la final a las 21:53:18 conservaron contador y fecha. |
| Heartbeat local | Tres consultas desde la Pi a `127.0.0.1`, a las 21:51:51, 21:51:53 y 21:51:55 CEST, devolvieron el mismo contador y fecha. La falta de frescura también está presente localmente. |
| Armado | El heartbeat almacenado tiene `base_mode.bits=9` (desarmado) y SmartRTL, pero es antiguo: no se presenta como una lectura actual del estado del vehículo. |
| Relojes | Pi menos PC: aproximadamente +0,249 s, con ida/vuelta de 0,633 s. No explica el atraso de decenas de segundos. No se ajustó ningún reloj. |
| Proceso | No se encontró un ejecutable activo `ardupilot_navigator64` en `/proc`. El contraste con `ps` mostró tres entradas `ardupilot_navig`, PID 1947, 31725 y 216827, todas en estado `Z` (zombi). No aportan un proceso activo ni descriptores I²C actuales. |
| Asignación activa de buses | El árbol de dispositivos mantiene `i2c-3` en GPIO6/GPIO7 e `i2c-4` en GPIO40/GPIO41. Se resolvieron las referencias `pinctrl-0`, sin inferir la asignación únicamente del archivo de arranque. |
| Cliente del kernel en `0x40` | No se encontró un cliente registrado en `3-0040` ni en `4-0040`. Esto no prueba ausencia de otros procesos de espacio de usuario; no habilitó las transacciones suspendidas. |
| Herramienta de lectura | `i2ctransfer` no está en el PATH del host consultado; sí existe en `/usr/sbin/i2ctransfer` dentro de `blueos-core`. No se ejecutó. |
| Archivo de firmware guardado | 3 993 824 bytes, ELF64 AArch64. SHA-256 `e0cede800da4bd895ec3d60f2d4ea68879e16f6da6998716440f8dded5ed736e`, idéntico al artefacto oficial 4.7.2 ya conservado, cuyo hash se recalculó. Es identidad del archivo almacenado, no de un proceso funcionando en esta ventana. |
| Selección de BlueOS | La API declara Navigator64 y firmware 4.7.2 STABLE. El detector instalado conserva SHA-256 `e0a81593c818d010575ab43230d76d0201bc4268105b499f37bae72ea28a44a1` y espera PCA9685 en bus 3 para Pi 5 y bus 4 para Pi 4. |

El [código oficial del commit identificado](https://github.com/ArduPilot/ardupilot/blob/fb773567896014da007bca58358704d4a0d8516f/libraries/AP_HAL_Linux/HAL_Linux_Class.cpp#L212-L213), recuperado de nuevo al PC, conserva `get_device_ptr(4, ...)` para Navigator. El [controlador I²C](https://github.com/ArduPilot/ardupilot/blob/fb773567896014da007bca58358704d4a0d8516f/libraries/AP_HAL_Linux/I2CDevice.cpp) abre ese número sin remapeo, y el [controlador PCA9685](https://github.com/ArduPilot/ardupilot/blob/fb773567896014da007bca58358704d4a0d8516f/libraries/AP_HAL_Linux/RCOutput_PCA9685.cpp) devuelve el búfer de órdenes. Estas son comprobaciones de código; no sustituyen los descriptores y las lecturas del chip que faltan en esta sesión.

## Bloqueo identificado y ensayo independiente

Mientras se realizaba esta inspección apareció en la documentación compartida el [ensayo directo de neutro en bus 3](2026-10-20-pwm3-neutro-bus3.md), ID `F1-PWM3-NEUTRO-20261020-214800`. Ese registro documenta una intervención independiente desde las 21:48 CEST, la parada intencionada de ArduPilot con el mismo contador 3898 y última fecha 21:49:44 CEST, y la preparación del PCA9685 para una ventana de neutro. Se conservó una copia fechada del documento como fuente.

Esto explica documentalmente la parada observada; no se atribuye a una avería ni a una caída de Cockpit. Las escrituras del ensayo independiente no pertenecen a esta inspección. No se leyeron los registros del chip para evitar interferir con su coordinación. Los valores `MODE1=0x11`, `SLEEP` y `FULL_OFF` de la [inspección anterior](2026-10-20-pwm3-controlador.md) siguen siendo históricos y no se presentan como valores actuales después de aquella preparación.

**Dictamen de esta repetición: inconcluso para el ArduPilot en ejecución.** La identidad del archivo, la selección fija de bus en el código, el detector de BlueOS y la asignación activa de GPIO respaldan el diagnóstico previo, pero no se repitió la comprobación completa proceso/bus/chip. No se acredita recuperación de PWM ni reconocimiento físico del neutro.

## Evidencias, estado final y siguiente paso

Evidencias en `local/registros/F1-PWM-I2C-20261020-215029/`: `session.json`, `operations.jsonl`, heartbeat remotos y locales, comparación de relojes, procesos y estados, árbol de dispositivos, identidad del archivo guardado y detector, comparación con el artefacto oficial, esquemas de la API, copias del código oficial y del registro de la intervención concurrente, `inspection-result.json` y `SHA256.json`. Se conservan las dos interrupciones iniciales por falta de frescura y los métodos usados para descartar el desfase de relojes. Credenciales utilizadas solo en memoria, sin incluirlas en comandos o evidencias.

**En repositorio:** este informe, síntesis e índice. **En el vehículo:** esta inspección no cambió configuración, firmware, servicios, GPIO o PWM; no hay cambios propios que revertir. La última consulta conserva heartbeat antiguo y ausencia de ejecutable activo. El estado del chip preparado pertenece al ensayo independiente y no se releyó aquí. **Tarea pendiente**, sin diagnóstico nuevo completo ni prueba de motores.

Para retomar, primero debe concluir el ensayo independiente y verificarse su recuperación por su responsable. Después repetir tres heartbeat frescos, crecientes y desarmados, confirmar proceso único e identidad del ejecutable y renovar la confirmación de aislamiento físico. Solo entonces recoger descriptores y ejecutar las lecturas individuales previstas en buses 3/4, comparándolas con telemetría fresca de PWM3. No interpretar como valores de arranque los registros que haya dejado el ensayo de neutro. Arrancar ArduPilot o restaurar el chip no está autorizado por esta inspección.

Comprobaciones documentales: `python .github/checks/check_repository.py` con Python 3.12 pasó sobre 65 archivos y 186 enlaces/anclas, junto con sintaxis/configuración, patrones de secretos, regeneración de misiones y visor. `git diff --check` de los documentos versionados afectados no señaló errores. Estas comprobaciones no validan el PWM ni eliminan el bloqueo operativo descrito.
