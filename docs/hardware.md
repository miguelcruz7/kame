# Hardware e interfaces de Kame

Este documento describe el montaje y la configuración **documentados**, no una comprobación en vivo. Consultar [estado observado](estado.md) antes de operar.

## Control y navegación

| Componente | Instalación documentada |
| --- | --- |
| Ordenador de a bordo | Raspberry Pi 5 con BlueOS 1.4.3 en la última lectura documentada. |
| Autopiloto | Navigator seleccionado como `Navigator64`, **compilación local de ArduRover 4.7.2**, ELF64 AArch64, instalada el 2026-10-20. SHA-256 `5cf0eb0ddc6fafc378862883614948dfc5f90f9e63bf4fd1e8ff5cdd6ca6a537`; selecciona bus 3 para el PWM en Pi 5 y conserva el 4 real de la cámara. Inicialización y neutro comprobados tras instalar, reiniciar ArduPilot y el apagado/encendido posterior realizado por el usuario; ver [reparación y límites](historial/2026-10-20-pwm-pi5-reparacion.md). El binario oficial y 4.6.3 son antecedentes históricos. Montaje y orientación detallados debajo. |
| GPS | ArduSimple simpleRTK2B Budget, u-blox ZED-F9P, conectado por USB. BlueOS lo asignaba al puerto D/Serial 2; alias `/dev/serial/by-path/platform-xhci-hcd.0-usb-0:2:1.0`, dispositivo `/dev/ttyACM0`. El 2026-10-19 se releyeron `GPS1_TYPE=2` (u-blox) y `SERIAL2_PROTOCOL=5` (GPS); el valor NMEA `GPS1_TYPE=5` fue anterior. Tras un `NO_GPS` temporal después del reinicio, a las ~19:31 CEST había `DGPS` con 15 satélites. |
| Brújula | Según el usuario el 2026-10-20, MMC5983 desconectada por incompatibilidad con Raspberry Pi 5 en esta instalación; únicamente AK09915 restante, sin errores comunicados. Las ranuras MMC5983/AK09915 del 2026-10-16 corresponden al montaje anterior; no se han releído prioridades ni parámetros actuales. Ver [montaje comunicado](historial/2026-10-20-brujula-mmc5983.md) y [actualización operativa](historial/2026-10-20-estado-operativo.md). |

## Navigator: montaje y calibración

**Montaje comunicado por el usuario el 2026-10-19:** placa con la cara superior hacia arriba, flecha `FRONT` hacia proa y unos 10–13° de inclinación proa abajo respecto al plano del casco en su posición normal de navegación. El ángulo es aproximado.

**Configuración leída por Wi-Fi `KAME` tras guardarla el usuario y reiniciar ArduPilot:** `AHRS_ORIENTATION=101` (`Custom 1`), `CUST_ROT_ENABLE=1`, `CUST_ROT1_PITCH=-13°`, `CUST_ROT1_ROLL=0°`, `CUST_ROT1_YAW=0°`, `AHRS_TRIM_Y=0`. `101` selecciona la rotación personalizada; los grados están en `CUST_ROT1_PITCH`. Con el casco derecho y quieto, cinco lecturas frescas de `ATTITUDE` y `AHRS2` coincidieron cerca de roll −0,7° y pitch +0,1°. Esto verifica la corrección de montaje **en reposo**, no una calibración completa.

**Calibración comunicada el 2026-10-20:** el usuario confirmó que la calibración de acelerómetros está completada con la orientación actual. Se registra como confirmación del usuario; no se recibieron nuevos parámetros ni archivos de calibración. Sustituye el pendiente anterior, conservado en el [registro de orientación del 2026-10-19](historial/2026-10-19-orientacion-navigator.md). Ver [actualización operativa](historial/2026-10-20-estado-operativo.md).

En cada sesión se comprueban actitud, rumbo, GPS y prearm actuales siguiendo [preparación](preparacion.md). La ausencia de errores de brújula no es una nueva medida independiente de rumbo. El armado transitorio de origen desconocido pertenece a aquella sesión histórica; se conserva en su registro sin presentarlo como fallo actual ni atribuirle una causa resuelta. La fase y los pendientes operativos se consultan en [estado.md](estado.md).

## Cámara y vídeo

- Cámara Waveshare IMX462 IR-CUT Camera (A) por CSI. El archivo `/boot/firmware/config.txt` contenía `dtoverlay=imx462`. `rpicam` la enumeró como `imx290`, nombre interno compatible con el overlay observado.
- Captura fija verificada a 1920×1080. En pruebas locales anteriores sostuvo MJPEG a 1280×720/15 y 30 FPS, y 1920×1080/30 y 60 FPS. El control por GPIO del IR-CUT sigue sin cableado verificado.
- BlueOS 1.4.3 no ofrecía una fuente CSI utilizable en Video Manager. La instalación usa MediaMTX con cámara `rpiCamera` para `/cam` y otra instancia para `/yolo`.
- La configuración documentada de `/cam` usa H.264 1920×1080 con objetivo de 20 FPS y bitrate 3,5 Mb/s. El stream `/yolo` es H.264 960×540 a 8 FPS nominales. Ver [guía de vídeo](../software/video/README.md).

## Red y puertos

| Enlace | BlueOS | Cámara original | Vídeo YOLO |
| --- | --- | --- | --- |
| Wi-Fi `KAME` | `http://192.168.42.1/` | `rtsp://192.168.42.1:8554/cam` | `rtsp://192.168.42.1:8556/yolo` |
| Ethernet `eth0` | `http://192.168.2.2/` | `rtsp://192.168.2.2:8554/cam` | `rtsp://192.168.2.2:8556/yolo` |
| ZeroTier/4G | `http://10.133.182.55/` | `rtsp://10.133.182.55:8554/cam` | `rtsp://10.133.182.55:8556/yolo` |

El módem Luat Air780EG usa `eth1` (`192.168.10.2/24`, gateway `192.168.10.1`) y puerto AT `/dev/ttyACM1`. No enviar comandos de módem a `/dev/ttyACM0`: pertenece al GPS. Las instancias RTSP escuchaban en `0.0.0.0:8554` y `0.0.0.0:8556` desde el cambio del 2026-10-16; `0.0.0.0` es una dirección de escucha, no una URL para clientes. El detector usa `127.0.0.1` para leer y publicar RTSP dentro de la Pi.

La red ZeroTier privada tiene Raspberry `10.133.182.55` y PC `10.133.182.131`. Su ID y las identidades de los nodos se conservan en `local/red.md`, excluido de Git. Detalles de instalación y diagnóstico: [acceso móvil](../software/conectividad/README.md).

## Propulsión y configuración

El 2026-10-20 el usuario confirmó T200 + Basic ESC de Blue Robotics en el lado derecho, asignado a PWM3; al cerrar la prueba supervisada se retiró su cable de control. El conjunto funcionaba con un receptor RC directo según su observación previa. El 2026-10-21 comunicó que «ya funcionan los motores», sin detallar todavía la prueba de cada lado. Antes se comunicaron también un ESC Spektrum SPMXME1A de 100 A y batería 4S, sin identificar completamente el equipo de cada lado. No se ha demostrado que existan sensores de RPM, encoders ni telemetría ESC.

| Lado | Conexión y configuración documentadas | Pendiente |
| --- | --- | --- |
| Derecho | Actualización del 2026-10-20: PWM3 comunicado por el usuario; `SERVO3_FUNCTION=74` releído. Sustituye la conexión histórica a PWM2. Con el [firmware corregido instalado](historial/2026-10-20-pwm-pi5-reparacion.md), el usuario confirmó dos pitidos adicionales y ningún movimiento en la prueba de neutro. | Documentar por separado las condiciones y respuesta de giro de este lado. Al cierre del ensayo de neutro, control retirado; ArduPilot se leyó desarmado y el chip despierto. |
| Izquierdo | `SERVO1_FUNCTION=73` releído el 2026-10-20. | Confirmar cableado físico a PWM1, equipos del lado y condiciones del funcionamiento comunicado el 2026-10-21. |

Se releyeron `FRAME_CLASS=2`, `FRAME_TYPE=0` y PWM normal el 2026-10-20. La [discordancia original entre los buses 4 y 3](historial/2026-10-20-pwm3-controlador.md) se corrigió con el firmware local: ArduPilot abre ahora `i2c-3`; PWM3 reporta 1500 µs y el chip contiene 306 cuentas, nominalmente unos 1494 µs a 50 Hz. El ESC reconoció ese neutro según el usuario; no se midió la forma de onda con instrumento. Las pruebas históricas a 1550 µs se aceptaron sin giro observado; ver [motores/ESC](historial/2026-10-19-motores-esc.md). La telemetría por sí sola no acredita salida eléctrica ni alimentación del ESC. Los [snapshots del 16 de octubre](historial/parametros/README.md) preceden a estos ajustes.

## Responsabilidades y orientación de datos

ArduPilot controla propulsión y estimación del vehículo; BlueOS proporciona servicios e interfaces; Cockpit permite supervisión y mando. La cadena de vídeo es cámara → MediaMTX `/cam` → YOLO → MediaMTX `/yolo` → Redirect/WebRTC → Cockpit. ZeroTier es un enlace de acceso y no prueba estado de sensores.

Antes de integrar autonomía/ROS 2, documentar proa y ejes del casco, marcos de sensores, unidades, conversiones NED/ENU y marcas de tiempo. La rotación de montaje leída no sustituye calibración. Las imágenes y registros originales están indexados en el [inventario local](historial/recursos.json).
