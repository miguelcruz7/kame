# PWM3: ensayo directo de neutro en bus 3 — 2026-10-20

**ID:** `F1-PWM3-NEUTRO-20261020-214800`. Intervención 21:48–21:58 CEST (Europe/Madrid) a petición del usuario: «podemos hacer una prueba rapida?». Objetivo: comprobar reconocimiento del neutro del Basic ESC + T200 por PWM3 usando el bus físico identificado, sin instalar firmware, armar ni ordenar giro. **Resultado comunicado: dos pitidos adicionales, correspondientes a señal y neutro, sin movimiento. ArduPilot recuperado y desarmado; salida de prueba apagada.**

## Autorización, entorno y respaldo

El usuario confirmó en esta sesión: «Todo confirmado; controles desconectados», en respuesta a la comprobación conjunta de supervisión junto al barco, barco sujeto, hélice despejada, corte de batería accesible y controles de todos los ESC retirados del Navigator. La potencia del ESC puede seguir conectada; durante la preparación los controles permanecen aislados. La reconexión exclusiva del T200 se solicita cuando el chip ya está preparado y deshabilitado.

Raspberry Pi 5, BlueOS 1.4.3, Navigator64 y ArduRover 4.7.2 STABLE; acceso por API BlueOS y SSH sobre ZeroTier/4G. El commit del repositorio y cambios locales preexistentes están en `session.json`; no se cambió de rama ni se publicó código. Se guardaron los 915/915 parámetros antes de intervenir, identidad de placa/firmware y estado de WebAssistant deshabilitado. Se conserva el respaldo previo del ejecutable y configuración en `F1-PWM3-WEBASSISTANT-20261020-210740`, referenciado en la evidencia local.

El acceso directo al PCA9685 se limita al diagnóstico: la [inspección del controlador](2026-10-20-pwm3-controlador.md) identificó el chip en bus 3 y el firmware accediendo al bus 4; [WebAssistant](2026-10-20-pwm3-webassistant.md) no arranca. No hay una interfaz de alto nivel operativa que permita este ensayo en la instalación actual. Se detuvo ArduPilot mediante su API instalada antes de escribir en el chip; se verificaron proceso ausente y heartbeat detenido (contador 3898, última actualización 21:49:44 CEST). Un error local de lectura de la estructura JSON del contador se corrigió y quedó registrado; no había enviado escrituras PWM.

## Configuración y secuencia

Solo dirección I²C `0x40` en bus 3, sin barridos ni cambios globales de buses. La lectura individual de registros verificó los 16 canales en `FULL_OFF`, `MODE1=0x11`, `MODE2=0x04`, `PRE_SCALE=0x1e` y PWM3 `00 00 00 10`. GPIO26 se leyó como salida a nivel bajo; no se cambió GPIO.

La preparación a las 21:50:20 CEST mantuvo `SLEEP` y `FULL_OFF`: seleccionó reloj externo (`MODE1=0x51`), prescaler 119 (`0x77`) y solo el canal de PWM3 (LED2) con 307 cuentas, todavía apagado (`00 00 33 11`). A 24,576 MHz corresponde nominalmente a 50 Hz y 1499,023 µs. Los demás canales no se modifican. La [hoja de datos del PCA9685](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf) define la secuencia de reloj, prescaler y apagado. El reloj de Navigator se corresponde con el usado por su [controlador de ArduPilot](https://github.com/ArduPilot/ardupilot/blob/fb773567896014da007bca58358704d4a0d8516f/libraries/AP_HAL_Linux/HAL_Linux_Class.cpp).

El programa preparado permite únicamente ese neutro durante unos 10 segundos y apaga después con `FULL_OFF` antes de `SLEEP`. Un segundo proceso a bordo ejecuta el mismo apagado a los 12 segundos como respaldo, independiente de la conexión SSH. Su comparación inicial de lectura produjo el error descrito debajo; ambos llegaron a escribir apagado y reposo. La supervisión física y el corte de batería siguen siendo necesarios; no es una garantía frente a fallos del chip, del SO o de la alimentación.

## Resultado y apagado

El usuario confirmó «T200 conectado a PWM3 correctamente; listo para los 10 segundos». La salida se habilitó a las **21:53:28 CEST** con `MODE1=0x41`, prescaler 119 y PWM3 `00 00 33 01`; los registros activos se leyeron correctamente. Se ordenó `FULL_OFF` a las **21:53:38 CEST**, aproximadamente diez segundos después. El usuario comunicó: **«2 pitidos cortos despues de los 3 de arranque»**. Según la [secuencia del fabricante](https://bluerobotics.com/learn/thruster-usage-guide/#esc-beeps), corresponde a señal y reconocimiento del neutro. Después confirmó expresamente ausencia de movimiento. Sin instrumento no se mide la forma de onda.

**Conclusión permitida:** con el acceso correcto por bus 3, el conjunto Navigator/PWM3/cableado conectado/Basic ESC reconoce el neutro según la observación presencial del usuario. Esto refuerza la discordancia de bus de ArduPilot como causa de que con ese firmware no inicialice. No valida giro, control desde ArduPilot, otros canales, navegación ni funcionamiento prolongado. No se instaló una corrección del firmware.

El programa principal y el respaldo a los 12 segundos confirmaron `FULL_OFF` y escribieron `SLEEP`, pero su comparación inicial de `MODE1` esperaba `0x51` y leyó `0xd1`: el chip también tenía activo `RESTART` (bit 7, estado interno). La comparación demasiado estricta interrumpió la restauración restante; **no dejó PWM activo**. Se corrigió la comparación únicamente para ese bit de estado y, sin repetir la ventana de señal, se completó la restauración a las **21:54:51 CEST**. Lecturas nuevas verificaron los 16 canales apagados, chip dormido, PWM3 `00 00 00 10` y prescaler original `0x1e`. Las versiones del programa, los dos errores y la repetición del apagado se conservan íntegros.

**Límite de reversión:** los registros de PWM3 y el prescaler están restaurados, todos los canales apagados y el chip dormido. `MODE1` queda en `0xd1` frente a `0x11` inicial: `EXTCLK` seleccionado y `RESTART` observado, además de `SLEEP` y `ALLCALL`. `RESTART` no habilita una salida dormida ni anula `FULL_OFF`. `EXTCLK` solo puede borrarse retirando alimentación del chip o mediante reset software; no se ha enviado un reset general del bus ni reiniciado la Raspberry.

## Recuperación y evidencias

El usuario confirmó «Control retirado; todos desconectados y no hubo movimiento». Se verificó que programa y respaldo habían terminado; se arrancó ArduPilot mediante `POST /ardupilot-manager/v1.0/start`. Hubo heartbeat fresco y creciente a las 21:57:14/21:57:17 CEST y una nueva lectura a las **21:58:00 CEST**, contador 3951, Manual, **desarmado**, `MAV_STATE_ACTIVE`. La API confirmó Navigator64 y firmware 4.7.2 STABLE; el ejecutable conserva el SHA-256 `e0cede800da4bd895ec3d60f2d4ea68879e16f6da6998716440f8dded5ed736e`. WebAssistant sigue deshabilitado.

Se respaldaron nuevamente 915/915 parámetros: **110 parámetros de salidas, motor, bastidor y seguridad comparados sin cambios**. Las cuatro diferencias son valores actualizados automáticamente: `COMPASS_DEC`, `BARO1_GND_PRESS`, `STAT_RUNTIME` y `STAT_BOOTCNT` (38 → 39); no se restauraron valores automáticos antiguos. Una lectura directa después del arranque volvió a confirmar `MODE1=0xd1`, chip dormido y los 16 canales en `FULL_OFF`. No queda una señal de neutro permanente ni un programa de control activo.

Datos crudos en `local/registros/F1-PWM3-NEUTRO-20261020-214800/`: `session.json`, respaldos de parámetros y comparación, `operations.jsonl`, código ejecutado inicial y corrección del comparador, registros antes/durante/después, `run.log`, `guard.log`, observación presencial, estado de recuperación y `SHA256.json`. Los archivos temporales de diagnóstico a bordo permanecen en `/tmp/F1-PWM3-NEUTRO-20261020-214800/`, sin servicio ni arranque automático. Los binarios/configuración previos se conservan en el respaldo enlazado; los datos locales privados deben preservarse para recuperar esa evidencia.

**Estado final:** prueba de inicialización positiva según el usuario, sin giro, controles desconectados, chip apagado y ArduPilot original funcionando desarmado. La selección incorrecta de bus del firmware sigue sin corregirse; no reconectar para operar suponiendo que este ensayo la haya reparado. La ausencia temporal de heartbeat fue intencionada y no se atribuye al fallo independiente de Cockpit.

**Pendiente fuera del alcance de este ensayo:** preparar y validar una corrección del controlador para Pi 5; una instalación y posterior ensayo necesitan su propia autorización. No se continuó con giro, navegación o cambios de firmware.

Comprobaciones locales: revisión del alcance/documentos, `git diff --check` y comprobador portátil del repositorio con Python 3.12.14. Estas comprobaciones no acreditan forma de onda ni navegación física.
