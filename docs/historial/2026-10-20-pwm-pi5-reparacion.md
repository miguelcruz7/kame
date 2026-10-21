# Reparación del bus PWM de Navigator64 en Pi 5 — 2026-10-20

**ID:** `F1-PWM-PI5-FIX-20261020-220937`. Intervención iniciada a las 22:09 CEST (Europe/Madrid), continuada en una conversación nueva a petición del usuario mediante el traspaso local del mismo ID. Objetivo: compilar e instalar ArduRover 4.7.2 Navigator64 con la selección de bus PCA9685 corregida para Pi 5, verificar su inicialización y repetirla al reiniciar solo ArduPilot; terminar con un ensayo supervisado de neutro de PWM3 de diez segundos como máximo. Esta entrada distingue el procedimiento de actualización, las comprobaciones directas y las observaciones comunicadas por el usuario.

## Autorización y alcance

El usuario aprobó el plan de reparación y pidió continuar su implementación en una conversación nueva. Antes de instalar, confirmó en esta conversación «Todo confirmado; controles retirados» para supervisión junto al barco, casco sujeto, hélice despejada, corte de batería accesible y controles de todos los ESC retirados del Navigator. La API de instalación puede arrancar ArduPilot incluso si devuelve error; los controles permanecen retirados durante toda la preparación, instalación y reinicio de comprobación.

No se autoriza armado, orden de giro, navegación, reinicio de Raspberry, reparación de WebAssistant, cambios de red ni calibraciones. No se publica ni integra código. La prueba física prevista conecta exclusivamente el T200/Basic ESC a PWM3, mantiene neutro y exige retirar el control al acabar. El posterior apagado y encendido de la alimentación fue realizado por el usuario, no por el asistente.

## Entorno, estado inicial y respaldos

Raspberry Pi 5, BlueOS 1.4.3, Navigator64, acceso por API BlueOS/MAVLink2REST y SSH con contraseña sobre ZeroTier/4G. PC Ubuntu 22.04/WSL x86_64. Repositorio Kame en `621a432c45de30500211aa906de82ccbda6cf549`, rama `codex/local-git-authorization-rules`, con cambios locales previos conservados y enumerados en `session.json`; no se cambió de rama.

Las lecturas nuevas a las 22:21 CEST confirmaron un único proceso original, PID 19257, SHA-256 `e0cede800da4bd895ec3d60f2d4ea68879e16f6da6998716440f8dded5ed736e`, con `/dev/i2c-4` y `/dev/i2c-1`. Chip físico en bus 3: `MODE1=0xd1`, prescaler 30 y los 16 canales en `FULL_OFF`, como al cierre del [ensayo directo anterior](2026-10-20-pwm3-neutro-bus3.md). No se escribió en el chip durante esta lectura.

A las 22:24 CEST, heartbeat fresco y desarmado, Hold y `MAV_STATE_CRITICAL`, PWM3 ordenado a 1500 µs. El último texto era «PreArm: Mode not armable». Este estado se observó antes de instalar la corrección; no se envió un cambio de modo ni se atribuyó su causa al parche.

Se conservaron los 915/915 parámetros y selección de placa/firmware/extensión. Se repitió correctamente el respaldo fresco que había fallado por SSH en la preparación: `ardupilot-manager-before.tar.gz`, 1 554 617 bytes, SHA-256 `1b43132b0c3167827254170077f006154730bc1565038b1c4645c26ee6dd9740`. Incluye ejecutable, `settings.json`, almacenamiento y scripts; excluye logs históricos. El almacenamiento se copió con ArduPilot activo y se complementa con la exportación completa MAVLink. Se extrajo el ejecutable original y verificó su hash para permitir recuperación mediante la misma API. Justo antes de instalar se repitieron la exportación completa de 915/915 parámetros y el respaldo de configuración en `ardupilot-manager-preinstall.tar.gz` (1 554 619 bytes; SHA-256 `9b946e0e7851bba9b1e3382979624f2b589a102eb3a06d965dec23639bc030ae`).

## Fuente y compilación

La [inspección del controlador](2026-10-20-pwm3-controlador.md) encontró al firmware original abriendo I²C 4 mientras el PCA9685 respondía en I²C 3. La [adaptación de BlueOS](2026-10-20-blueos-i2c-camara.md) no crea su enlace 4→3 porque el bus 4 ya existe y sirve a la cámara. Por eso se corrigió la elección del bus en ArduPilot, conservando el bus real de la cámara.

Base exacta de ArduPilot: `fb773567896014da007bca58358704d4a0d8516f`. El único cambio de fuente es `libraries/AP_HAL_Linux/HAL_Linux_Class.cpp`: `utilInstance.detect_linux_board_type() == LINUX_BOARD_TYPE::RPI_5 ? 3 : 4`. `UtilRPI` se construye antes que la salida Navigator en la misma unidad y su constructor detecta la placa. Se conservan dirección `0x40`, reloj de 24,576 MHz, GPIO26, canales, parámetros y conversión de pulsos. La revisión se hizo sobre ese commit y sus guías de contribución.

Se detuvo exclusivamente el grupo de descarga propio 16678 antes de copiar sus recursos desde NTFS a la carpeta Linux de WSL. El original queda preservado en `local/firmware-ntfs-preserved-F1-PWM-PI5-FIX-20261020-220937/`; `local/firmware` enlaza a la copia activa y `build-location.json` conserva su destino absoluto. No se eliminaron los recursos únicos ni el paquete de descarga interrumpido.

Receta en [software/firmware](../../software/firmware/README.md), GCC/G++ 11.4, Python 3.10.12 y dependencias fijadas. Se completaron los submódulos en los commits de la base. Se corrigieron tres problemas de la preparación inicial, conservando sus logs: bibliotecas de herramientas extraídas no localizadas, rutas absolutas ARM del enlazador sin `--sysroot`, y dependencia Python `pexpect` ausente. No eran fallos del parche C++ ni implicaron cambios en el barco.

## Cómo se actualizó el firmware

1. Se fijó el código de ArduPilot en el commit de la versión 4.7.2 instalada y se aplicó [un parche de una sola selección de bus](../../software/firmware/navigator-pi5-pwm.patch): 3 en Raspberry Pi 5 y 4 en las demás plataformas. No se modificaron canales, frecuencia, parámetros ni GPIO.
2. Se compiló `ardurover` para AArch64 desde WSL con GCC/G++ 11.4 y los submódulos de ese commit. Se guardaron ejecutable, manifiesto de herramientas y hashes; antes de instalar se contrastaron sus bibliotecas y símbolos con los del BlueOS del barco.
3. Se respaldaron ejecutable, configuración y 915 parámetros; con los controles ESC retirados, se envió **solo el ejecutable** por la API de ArduPilot Manager de BlueOS 1.4.3, seleccionando `Navigator64` y el campo multipart `binary`, sin adjuntar parámetros. La API detuvo y volvió a arrancar ArduPilot.
4. Se comparó el hash instalado con el compilado y se comprobaron proceso, bus I²C 3, registros del PCA9685, telemetría desarmada y parámetros. Después se reinició únicamente ArduPilot por su API y se repitieron las lecturas. La comprobación tras el apagado y encendido realizado posteriormente por el usuario figura más abajo.

## Resultado de compilación e instalación

La compilación terminó a las **22:57 CEST**, con las 1246 tareas completadas. Ejecutable local de 3 973 328 bytes, SHA-256 **`5cf0eb0ddc6fafc378862883614948dfc5f90f9e63bf4fd1e8ff5cdd6ca6a537`**. La comprobación ELF/ABI confirmó AArch64, intérprete `/lib/ld-linux-aarch64.so.1`, bibliotecas disponibles y ausencia de símbolos importados sin resolver frente a las bibliotecas recogidas del contenedor instalado. Esto acredita compatibilidad binaria comprobada, además del arranque observado posteriormente.

El usuario renovó la confirmación física a las **23:00:51 CEST**: «Confirmado; todos los controles retirados». La subida por `POST /ardupilot-manager/v1.0/install_firmware_from_file?board_name=Navigator64` empezó a las **23:00:59 CEST** y respondió **HTTP 200 a las 23:03:02 CEST**, con el campo `binary` y sin campo de parámetros. Se esperó su resultado antes de verificar, sin repetir la instalación. Una lectura durante la subida todavía encontró el original; las lecturas posteriores identificaron el parche tanto en el archivo instalado como en `/proc/<pid>/exe`.

La verificación inicial encontró un único proceso parcheado, PID **29503**, con `/dev/i2c-3` y `/dev/i2c-1` abiertos. Lecturas individuales del PCA9685 por bus 3: `MODE1=0x60` (reloj externo y autoincremento, sin reposo), `MODE2=0x04`, `PRE_SCALE=119` y PWM3 `00 00 32 01`: **306 cuentas, nominalmente 1494,140625 µs a 50 Hz**. MAVLink reportó 1500 µs, heartbeat fresco y vehículo desarmado. Los registros son lecturas del chip; no se utilizó osciloscopio para medir la forma de onda.

Se reinició **solo ArduPilot** por `POST /ardupilot-manager/v1.0/restart`. El proceso nuevo, PID **29843**, conservó el hash parcheado y el acceso al bus 3; reprodujo los mismos registros y neutro, con heartbeat fresco y desarmado. No se reinició la Raspberry ni se cambiaron parámetros, puertos, buses, GPIO, servicios de vídeo o configuración de arranque.

Se exportaron de nuevo **915/915 parámetros** tras instalar y tras el reinicio. Comparados con el respaldo inmediatamente anterior: **129 parámetros de salidas, motor, bastidor y seguridad sin cambios**. Las únicas diferencias fueron `COMPASS_DEC`, `BARO1_GND_PRESS`, `STAT_BOOTCNT` (39 → 41 tras los dos arranques) y `STAT_RUNTIME`; no se restauraron valores automáticos antiguos. Las dos exportaciones y comparaciones quedan conservadas por separado.

Tras la prueba de neutro, el último chequeo perdió temporalmente el acceso SSH y una lectura HTTP falló; el asistente no aplicó cambios durante esa interrupción. El usuario apagó y volvió a encender la alimentación. Una lectura directa a las **23:10:21 CEST** encontró un nuevo proceso, PID **370**, con el mismo SHA-256 parcheado y `/dev/i2c-3`; `MODE1=0x60`, prescaler 119 y PWM3 de 306 cuentas. El heartbeat avanzaba, el vehículo estaba desarmado y MAVLink seguía informando 1500 µs en PWM3. Esta lectura verifica que el firmware y el neutro reaparecieron tras ese encendido comunicado por el usuario; no se midieron varios ciclos ni se atribuye la pérdida temporal de acceso a una causa concreta.

## Prueba física y coexistencia con la cámara

Tras verificar la inicialización repetida, se indicó conectar exclusivamente el control del T200/Basic ESC a PWM3 durante un máximo de diez segundos, sin armar, y retirarlo al acabar. El usuario confirmó en esta conversación: **«Dos pitidos, sin movimiento y control retirado»**. Esto valida reconocimiento del neutro generado por ArduPilot según su observación presencial. No se midieron independientemente los instantes de conexión/desconexión ni se ordenó giro. Un monitor de aproximadamente 65 s recogió 37 muestras con heartbeat y salida frescos, desarmado y PWM3 reportado a 1500 µs; su ventana no se atribuye a los diez segundos exactos de conexión física.

La cámara continúa como cliente `imx290lqr` en el bus físico 4; los tres servicios de cámara/YOLO estaban activos sin reinicios contabilizados. `ffmpeg` no estaba disponible como comando del anfitrión; se utilizó OpenCV ya instalado en el entorno de YOLO para decodificar **diez fotogramas de 1920×1080** del RTSP local `/cam`, sin errores. Se cerró el lector al terminar. Acredita decodificación local con el firmware parcheado, no una nueva prueba visual de Cockpit ni estabilidad prolongada. El conflicto de la adaptación oficial de BlueOS está documentado en su [inspección independiente](2026-10-20-blueos-i2c-camara.md).

**Estado tras la última lectura directa del 2026-10-20:** corrección instalada y verificada tras instalación, reinicio de ArduPilot y un apagado/encendido del usuario. El ESC reconoció el neutro sin movimiento durante la prueba supervisada y el usuario retiró el control. ArduPilot se leyó desarmado generando neutro; el chip estaba despierto. WebAssistant continuaba deshabilitado. No se realizó una prueba controlada de giro, navegación ni funcionamiento prolongado. Una actualización futura puede sustituir este binario local: comprobar el hash, no solo el texto de versión 4.7.2.

**Comunicación posterior, 2026-10-21:** el usuario informa «ya funcionan los motores». Se conserva como observación comunicada por él, posterior al ensayo de neutro anterior. No se recibieron aún duración, modo, órdenes, valores PWM ni observación individual de cada lado; por ello la prueba por motor del [estado vigente](../estado.md) no se da por documentada con esta frase.

## Evidencias y recuperación

Datos crudos, scripts operativos, logs, respaldos y traspaso en `local/registros/F1-PWM-PI5-FIX-20261020-220937/`; fuente, paquetes del compilador, entorno y artefactos en `local/firmware/`. El manifiesto de compilación identifica commit, parche, submódulos, versiones, opciones y hashes. Conservar ambos conjuntos privados para poder recuperar la evidencia y el ejecutable.

Reversión preparada, sin ejecutar: controles retirados, detener ArduPilot por API y verificar proceso ausente; solo entonces apagar canales con `FULL_OFF` y dormir el chip, sin reset general I²C. Restaurar el ejecutable original por la API de instalación, omitiendo parámetros, y verificar hash y heartbeat desarmado. La parada del proceso por sí sola no borra el último PWM. No restaurar valores automáticos antiguos de sensores o estadísticas.
