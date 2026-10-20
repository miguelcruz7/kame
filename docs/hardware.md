# Hardware e interfaces de Kame

Este documento describe el montaje y la configuración **documentados**, no una comprobación en vivo. Consultar [estado observado](estado.md) antes de operar.

## Control y navegación

| Componente | Instalación documentada |
| --- | --- |
| Ordenador de a bordo | Raspberry Pi 5 con BlueOS 1.4.3 en la última lectura documentada. |
| Autopiloto | Blue Robotics Navigator64, ArduRover 4.6.3 en la última lectura. Montaje y orientación detallados debajo. |
| GPS | ArduSimple simpleRTK2B Budget, u-blox ZED-F9P, conectado por USB. BlueOS lo asignaba al puerto D/Serial 2; alias `/dev/serial/by-path/platform-xhci-hcd.0-usb-0:2:1.0`, dispositivo `/dev/ttyACM0`. El 2026-10-19 se releyeron `GPS1_TYPE=2` (u-blox) y `SERIAL2_PROTOCOL=5` (GPS); el valor NMEA `GPS1_TYPE=5` fue anterior. Tras un `NO_GPS` temporal después del reinicio, a las ~19:31 CEST había `DGPS` con 15 satélites. |
| Brújulas | MMC5983 en ranura 1 y AK09915 en ranura 2; tercera entrada duplicada deshabilitada en la lectura del 2026-10-16. El aviso `PreArm: Compasses inconsistent` persistía el 2026-10-19; la selección de sensores no demuestra calibración válida. |

## Navigator: montaje y calibración pendiente

**Montaje comunicado por el usuario el 2026-10-19:** placa con la cara superior hacia arriba, flecha `FRONT` hacia proa y unos 10–13° de inclinación proa abajo respecto al plano del casco en su posición normal de navegación. El ángulo es aproximado.

**Configuración leída por Wi-Fi `KAME` tras guardarla el usuario y reiniciar ArduPilot:** `AHRS_ORIENTATION=101` (`Custom 1`), `CUST_ROT_ENABLE=1`, `CUST_ROT1_PITCH=-13°`, `CUST_ROT1_ROLL=0°`, `CUST_ROT1_YAW=0°`, `AHRS_TRIM_Y=0`. `101` selecciona la rotación personalizada; los grados están en `CUST_ROT1_PITCH`. Con el casco derecho y quieto, cinco lecturas frescas de `ATTITUDE` y `AHRS2` coincidieron cerca de roll −0,7° y pitch +0,1°. Esto verifica la corrección de montaje **en reposo**, no una calibración completa.

**Antes de navegar:** repetir y verificar la calibración de acelerómetros de seis posiciones con esta orientación activa. La calibración anterior se hizo antes de configurar `Custom 1` y no se ha validado para el montaje actual. La calibración de acelerómetros no necesita fix GPS; el GPS se recuperó a `DGPS` a las ~19:31, aunque la posición no se contrastó externamente. Sigue pendiente resolver `PreArm: Compasses inconsistent`. En esa misma revisión hubo un **armado transitorio** (`base_mode=193`, `Throttle armed`) seguido de diez lecturas desarmadas; se desconoce su causa y si había alimentación de motores. Asegurar motores aislados antes de calibrar y mantener el barco fuera de operación hasta resolver los avisos. La secuencia, valores anteriores, lecturas y límites están en el [registro de orientación del 2026-10-19](historial/2026-10-19-orientacion-navigator.md). El estado más reciente debe releerse en [estado.md](estado.md).

## Cámara y vídeo

- Cámara Waveshare IMX462 IR-CUT Camera (A) por CSI. El archivo `/boot/firmware/config.txt` contenía `dtoverlay=imx462`. `rpicam` la enumeró como `imx290`, nombre interno compatible con el overlay observado.
- Captura fija verificada a 1920×1080. En pruebas locales anteriores sostuvo MJPEG a 1280×720/15 y 30 FPS, y 1920×1080/30 y 60 FPS. El control por GPIO del IR-CUT sigue sin cableado verificado.
- BlueOS 1.4.3 no ofrecía una fuente CSI utilizable en Video Manager. La instalación usa MediaMTX con cámara `rpiCamera` para `/cam` y otra instancia para `/yolo`.
- La configuración documentada de `/cam` usa H.264 1920×1080 con objetivo de 20 FPS y bitrate 3,5 Mb/s. El stream `/yolo` es H.264 960×540 a 8 FPS nominales. Ver [guía de vídeo](../yolo-cockpit/README.md).

## Red y puertos

| Enlace | BlueOS | Cámara original | Vídeo YOLO |
| --- | --- | --- | --- |
| Wi-Fi `KAME` | `http://192.168.42.1/` | `rtsp://192.168.42.1:8554/cam` | `rtsp://192.168.42.1:8556/yolo` |
| Ethernet `eth0` | `http://192.168.2.2/` | `rtsp://192.168.2.2:8554/cam` | `rtsp://192.168.2.2:8556/yolo` |
| ZeroTier/4G | `http://10.133.182.55/` | `rtsp://10.133.182.55:8554/cam` | `rtsp://10.133.182.55:8556/yolo` |

El módem Luat Air780EG usa `eth1` (`192.168.10.2/24`, gateway `192.168.10.1`) y puerto AT `/dev/ttyACM1`. No enviar comandos de módem a `/dev/ttyACM0`: pertenece al GPS. Las instancias RTSP escuchaban en `0.0.0.0:8554` y `0.0.0.0:8556` desde el cambio del 2026-10-16; `0.0.0.0` es una dirección de escucha, no una URL para clientes. El detector usa `127.0.0.1` para leer y publicar RTSP dentro de la Pi.

La red ZeroTier privada documentada es `ID_ZEROTIER_PRIVADO`, con Raspberry `10.133.182.55` y PC `10.133.182.131`. Detalles de instalación y diagnóstico: [acceso móvil](../mobile-access/README.md).
