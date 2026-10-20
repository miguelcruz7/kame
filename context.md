# Contexto general del proyecto Kame

Documento de incorporación para un agente nuevo. Resume el propósito, la arquitectura, las decisiones técnicas, el historial útil y el modo de colaborar. **No es un estado en vivo**: las instalaciones y lecturas que se describen como observadas corresponden a fechas concretas. Antes de operar, leer `AGENTS.md` y `docs/estado.md` y verificar el vehículo por el enlace disponible.

## Propósito y etapas

Kame es un vehículo de superficie basado en Raspberry Pi 5, autopiloto Blue Robotics Navigator64 y ArduRover. El proyecto integra navegación por waypoints, GPS u-blox, cámara, detección visual YOLO, BlueOS/Cockpit y acceso remoto móvil.

La secuencia prevista es:

1. Desarrollar y repetir misiones en SITL.
2. Validar sensores, enlaces y controles del vehículo con pruebas controladas.
3. Pasar a pruebas en el mar cuando las comprobaciones pendientes estén resueltas.

El objetivo actual de YOLO es mostrar detecciones como apoyo visual. No está validado como sistema de seguridad ni debe controlar navegación o motores.

## Arquitectura general

```text
Control y navegación
Navigator64 + ArduRover ↔ MAVLink ↔ BlueOS en Raspberry Pi 5 ↔ Cockpit / estación de control

Vídeo
Cámara CSI IMX462 → MediaMTX /cam → detector YOLO en Raspberry Pi → MediaMTX /yolo
                                                          ↓
                                BlueOS Video Streams / MAVLink Camera Manager → WebRTC → Cockpit

Acceso remoto
Internet móvil USB en Raspberry → ZeroTier → PC de control
```

Para consultar sensores, parámetros, servicios y logs, se prefiere una API documentada de BlueOS, MAVLink/MAVLink2REST o SSH. La interfaz web se usa cuando hace falta comprobar la imagen real dentro de Cockpit o cuando una operación no tiene una API fiable. Una lectura HTTP correcta, un endpoint RTSP activo o una fuente anunciada no prueban por sí solos que el vídeo WebRTC sea actual y visible en Cockpit.

## Hardware y software documentados

- Raspberry Pi 5 con BlueOS 1.4.3 en la última revisión registrada.
- Navigator64 con ArduRover 4.6.3 en la última revisión registrada.
- GPS ArduSimple simpleRTK2B Budget con receptor u-blox ZED-F9P por USB. Se asignó al puerto D / Serial 2 de BlueOS; el dispositivo se identificó como `/dev/ttyACM0`.
- Cámara Waveshare IMX462 IR-CUT por CSI. El sistema usa el overlay `imx462`; `rpicam` la enumera como `imx290`, nombre de la implementación del sensor/overlay.
- Módem Luat Air780EG por USB para Internet móvil. En la instalación documentada usa `eth1`; `/dev/ttyACM1` es su puerto AT. `/dev/ttyACM0` pertenece al GPS.
- BlueOS/Cockpit administra la presentación de vídeo y la telemetría. YOLO y MediaMTX se ejecutan como servicios Linux en la Raspberry.

Direcciones documentadas de BlueOS:

| Enlace | Dirección |
| --- | --- |
| Wi-Fi `KAME` | `http://192.168.42.1/` |
| Ethernet | `http://192.168.2.2/` |
| ZeroTier / 4G | `http://10.133.182.55/` |

Las direcciones pueden dejar de estar disponibles si cambia la red o el vehículo está apagado. No inferir que la Pi está caída por un solo enlace fallido.

## GPS y navegación

La configuración que permitió recuperar recepción el 2026-10-16 fue `GPS1_TYPE=5` (NMEA) y `SERIAL2_PROTOCOL=5` (GPS). Después se registró fix 3D con 12 satélites y, en otra lectura, DGPS con 12 satélites. Siete lecturas durante unos 30 segundos mantuvieron fix 3D; `GPS_RAW_INT` se recibió entonces alrededor de 5,5 Hz. Esa frecuencia de MAVLink no es necesariamente la tasa interna exacta del receptor.

El 2026-10-13 `GPS_RAW_INT` estaba fresco, pero indicaba `NO_GPS`, 0 satélites y coordenadas nulas. La causa de aquella pérdida no quedó determinada. Por ello, tratar el fix del 16 de octubre como evidencia histórica, no como estado actual. Un estado DGPS tampoco demuestra RTK fijo; no hay en los documentos una cadena de correcciones RTCM/NTRIP validada.

Se registraron avisos de brújula `PreArm` relacionados con diferencia de campo magnético y calibración/reinicio. Las lecturas del 16 de octubre identificaron MMC5983 como brújula primaria y AK09915 secundaria, pero eso no demuestra que la calibración sea válida hoy. Verificar GPS, posición y texto completo de los avisos antes de usar modos dependientes de navegación.

## Cámara, vídeo y YOLO

La fuente CSI no aparecía como una entrada utilizable en Video Manager de BlueOS 1.4.3. Se implementó una ruta estable mediante MediaMTX:

- `/cam`: cámara original H.264, objetivo documentado 1920×1080/20 FPS y 3,5 Mb/s.
- YOLO26n NCNN FP16 en Raspberry Pi, entrada 320×320; detecta clases COCO `person` y `boat`, con `conf=0.15`.
- `/yolo`: imagen anotada H.264, 960×540 y 8 FPS nominales; la última prueba registrada rondó 7,4–8 inferencias/s.
- BlueOS Video Streams anuncia una sola fuente Redirect de YOLO para Cockpit. `/cam` sigue existiendo como RTSP y como entrada al detector.

La cámara probó capturas fijas y vídeo MJPEG en varias resoluciones/FPS. El control por software del IR-CUT no está validado porque falta confirmar cableado a GPIO.

La integración ha verificado decodificación, disponibilidad de fuentes, estabilidad del proceso durante pruebas y visualización de YOLO en Cockpit en una sesión concreta. No hay validación de precisión/recall ni pruebas representativas concluidas de personas/barcos, distancias, noche, reflejos o falsas alarmas. Una detección positiva aislada no confirma un acierto.

## Acceso remoto móvil

El Air780EG proporcionó Internet desde la Pi. ZeroTier conecta la Pi y el PC mediante una red privada; en una prueba con Ethernet desconectado se accedió a BlueOS, SSH y RTSP por ZeroTier. El enlace se marcó `RELAY`, con latencia y caudal variables; dos streams simultáneos se acercaron al caudal de subida 4G medido. La configuración posterior dejó YOLO como único stream anunciado en Cockpit.

El PIN de SIM y la contraseña SSH se mantienen en la sección de credenciales de `AGENTS.md`, según la instrucción del usuario. No copiarlos a este resumen ni imprimirlos innecesariamente. El desbloqueo de la SIM tiene servicio/timer; aún no figura una verificación completa de apagado y reconexión física del módem.

## SITL y experimentación

`sitl/start.sh` inicia ArduRover con modelo `motorboat-skid`, velocidad de simulación 1 y posición inicial configurada, además de MAVLink2REST local. Usa `--wipe`, por lo que reinicia los parámetros persistidos de SITL al arrancar. Necesita entorno Bash/Linux, los binarios de `sitl/bin/` y fuentes ArduPilot, por defecto en `$HOME/ardupilot` (se puede indicar `ARDUPILOT_DIR`). `sitl/generate_missions.py` genera dos misiones de ejemplo `.cmp` alrededor del origen configurado.

Todavía no hay en esta documentación un sistema único que agrupe cada ensayo con misión, parámetros antes/después, log DataFlash `.bin`, telemetría `.tlog`, vídeo Cockpit y eventos/detecciones YOLO. Para comparar pruebas, conservar esos elementos bajo un ID común y anotar hora, enlace, condiciones, cambio probado y resultado. Los logs del autopiloto sirven para analizar posición, velocidad, navegación y salidas; Cockpit puede grabar vídeo y subtítulos de telemetría en el dispositivo de control.

## Historial y cuestiones abiertas

- **2026-10-09:** workaround CSI→RTSP y primera integración YOLO. La prueba inicial fue a 2 inferencias/s; no verificó detección positiva.
- **2026-10-13:** caídas de Ethernet y pérdida de acceso a la Pi; hubo apagado/encendido forzado reportado por el usuario. No se estableció causa raíz. En esa fecha se observó `NO_GPS` repetido.
- **2026-10-16:** se recuperó el GPS con los parámetros NMEA/GPS citados; se actualizó YOLO a 8 FPS y se dejó como único vídeo de Cockpit; se probó acceso móvil por ZeroTier. También se documentaron avisos de brújula y se perdió conectividad durante lecturas posteriores.

Pendientes principales en el último estado documentado:

1. Releer en vivo heartbeat, armado, GPS, posición y avisos de brújula antes de operar.
2. Confirmar vídeo actual dentro de Cockpit por el enlace que se vaya a usar (Wi-Fi, Ethernet o ZeroTier/4G).
3. Validar YOLO con escenas positivas y negativas conocidas; tratarlo como prototipo visual.
4. Verificar recuperación tras ciclo físico del módem/SIM y caracterizar latencia/caudal móvil.
5. Si reaparecen las caídas de red/sistema, recoger logs locales/por consola antes de atribuir causa.
6. Completar primero SITL y luego pruebas de navegación y motores controladas; no pasar a pruebas en el mar con las comprobaciones anteriores pendientes.

La última síntesis verificable del vehículo está en [`docs/estado.md`](docs/estado.md). El [historial de orientación del Navigator del 2026-10-19](docs/historial/2026-10-19-orientacion-navigator.md) registra los parámetros de montaje previos a una nueva calibración de acelerómetros y sus límites. Las observaciones históricas proceden de sesiones distintas y no constituyen una lectura simultánea.

## Guía de lectura para un agente nuevo

1. `AGENTS.md`: reglas operativas, inspección inicial, forma preferida de usar APIs/MAVLink/SSH, límites y credenciales documentadas.
2. `docs/estado.md`: última evidencia disponible y comprobaciones pendientes.
3. `docs/hardware.md`: conexiones, interfaces, nombres de dispositivo y direcciones.
4. README del subsistema en el que se vaya a trabajar: `sitl/`, `yolo-cockpit/`, `mobile-access/` o `navigator-imu-viewer/`.
5. `docs/historial/README.md` y entradas fechadas para reconstruir decisiones, incidentes, resultados y respaldos.

### Reglas esenciales

- Empezar con inspección de solo lectura y confirmar que cada lectura es fresca, indicando fecha y enlace.
- Priorizar API documentada, MAVLink/MAVLink2REST y SSH para datos estructurados; usar la interfaz cuando haga falta verificar algo visual como el WebRTC de Cockpit.
- Antes de un cambio autorizado, guardar el valor/configuración vigente; aplicar solo lo acordado, volver a leer el estado y registrar resultado y reversión.
- No cambiar parámetros, firmware o puertos, reiniciar, armar ni accionar motores sin autorización explícita y comprobación de seguridad. No operar con avisos de brújula sin resolver o GPS no validado.
- Preservar la ruta original `/cam` si se trabaja en YOLO; los procedimientos de despliegue/reversión están en `yolo-cockpit/README.md`.
- Actualizar `docs/estado.md` solo con observaciones verificables y añadir las mediciones extensas al historial fechado.
