# PWM3: discordancia del bus I²C de ArduPilot — 2026-10-20

**ID:** `F1-PWM3-CONTROLADOR-20261020-212528`. Inspección de solo lectura desde las 21:25 CEST, Europe/Madrid, solicitada por el usuario después del [fallo de arranque de WebAssistant](2026-10-20-pwm3-webassistant.md). Objetivo: revisar el controlador PWM de ArduPilot sin osciloscopio, sin cambiar servicios, parámetros, firmware, GPIO ni valores PWM.

## Entorno y método

Raspberry Pi 5 Model B Rev 1.1, kernel `6.6.31+rpt-rpi-2712`, BlueOS 1.4.3, Navigator64 y ArduRover 4.7.2; `AUTOPILOT_VERSION` identifica el commit `fb773567`. Acceso por HTTP/MAVLink2REST y SSH sobre ZeroTier/4G. El commit del repositorio y los cambios locales preexistentes se conservan en `inspection.json`. No se creó una rama, publicó ni integró código.

Se consultaron procesos, descriptores de dispositivos abiertos, configuración de arranque y árbol de dispositivos vigente. Para contrastar el bus usado por el autopiloto con el chip físico se hicieron lecturas dirigidas de registros del PCA9685 en la dirección conocida `0x40`. Esta comprobación no está disponible en la telemetría de alto nivel y permite distinguir el valor ordenado del estado del chip; justifica el acceso de diagnóstico a bajo nivel. Se usaron transacciones combinadas `i2ctransfer` que seleccionan el registro y leen su contenido, sin escribir valores de configuración o PWM, sin barridos del bus ni detener ArduPilot.

## Hallazgos directos

| Comprobación | Resultado |
| --- | --- |
| Telemetría | Heartbeat fresco y desarmado; `SERVO_OUTPUT_RAW.servo3_raw=1500`. No se envió un cambio de modo. |
| Dispositivos abiertos por ArduPilot | `/dev/i2c-4` y `/dev/i2c-1`; ningún descriptor de `/dev/i2c-3`. |
| Bus del PCA9685 | La dirección `0x40` respondió en `/dev/i2c-3`; las tres lecturas dirigidas en `/dev/i2c-4` fallaron con `Remote I/O error`. |
| Asignación física vigente | `i2c-3` usa GPIO6/GPIO7; `i2c-4` usa GPIO40/GPIO41, según el árbol de dispositivos del sistema. El arranque configura `i2c3-pi5`. |
| `MODE1`, registro `0x00` | `0x11`: bit `SLEEP` activo y autoincremento desactivado. |
| `MODE2`, registro `0x01` | `0x04`. |
| PWM3, registros `0x0e`–`0x11` | Lecturas individuales: `00 00 00 10`; `LED2_OFF_H` tiene el bit `FULL_OFF` activo. PWM3 está deshabilitado en el chip. |
| `PRE_SCALE`, registro `0xfe` | `0x1e`. No se interpreta como una frecuencia medida porque el chip está en reposo. |

La primera lectura en bloque devolvió ceros repetidos para PWM3. Al comprobar que `MODE1` no tiene autoincremento se repitió cada dirección individualmente; **la evidencia válida para los cuatro registros es la lectura individual**, que identifica `FULL_OFF`. No se habilitó autoincremento para obtenerla.

## Contraste con el controlador

El [código del commit anunciado por el firmware](https://github.com/ArduPilot/ardupilot/blob/fb773567/libraries/AP_HAL_Linux/HAL_Linux_Class.cpp) construye el controlador PCA9685 de Navigator con `get_device_ptr(4, ...)`, reloj externo de 24,576 MHz y GPIO26 como habilitación. Esto coincide con el descriptor observado hacia `i2c-4`, mientras el chip real responde en `i2c-3`. El [controlador I²C](https://github.com/ArduPilot/ardupilot/blob/fb773567/libraries/AP_HAL_Linux/I2CDevice.cpp) abre el número de bus recibido sin remapearlo para Pi 5.

Además, el [controlador PCA9685](https://github.com/ArduPilot/ardupilot/blob/fb773567/libraries/AP_HAL_Linux/RCOutput_PCA9685.cpp) devuelve en `read()` su búfer de órdenes y no una lectura del chip; su envío de valores no propaga el resultado de `transfer()`. Por tanto, un valor MAVLink de 1500 µs puede coexistir con fallos de comunicación hacia el dispositivo.

**Conclusión:** hay una discordancia bloqueante entre el bus que utiliza el firmware instalado y el bus físico del PWM en esta Pi 5. El chip no tiene configurado el neutro reportado: está en reposo y PWM3 en `FULL_OFF`. Es una causa concreta suficiente para explicar la ausencia de inicialización del ESC con Navigator; no verifica todavía cableado externo, forma de onda ni respuesta después de corregirla. Es un problema distinto del fallo GPIO de WebAssistant.

## Evidencia y estado final

Datos en `local/registros/F1-PWM3-CONTROLADOR-20261020-212528/`: `system-controller.json`, `bus-pin-configuration.json`, lecturas iniciales y `pca9685-individual-registers.json`, mensajes MAVLink, `inspection.json` y `SHA256.json`. Se conservan tanto la lectura inicial como la repetición correcta, con su límite indicado arriba.

No se cambiaron parámetros, asignaciones de bus, firmware, servicios, señales de habilitación o valores PWM. ArduPilot siguió funcionando y se releyó desarmado. WebAssistant no se reactivó. No hay cambios operativos que revertir en esta inspección. Las comprobaciones del repositorio no acreditan funcionamiento eléctrico.

**Siguiente paso pendiente:** preparar una corrección de la selección del bus PWM para Pi 5, preservando el ejecutable y configuración respaldados; instalarla y probar únicamente neutro dentro de una intervención expresamente autorizada y con aislamiento físico confirmado. No modificar a ciegas la numeración global de buses ni considerar que reparar WebAssistant corrige el controlador de ArduPilot. Tras la corrección habrá que verificar registros y reconocimiento del neutro por el ESC; una medida de forma de onda seguirá siendo una comprobación independiente.
