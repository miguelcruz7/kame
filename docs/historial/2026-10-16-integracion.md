# 2026-10-16 · GPS, vídeo, brújulas y acceso remoto

Registro de observaciones y cambios del día. Las comprobaciones sucedieron en sesiones distintas y no equivalen a un estado simultáneo. Consultar [estado observado](../estado.md) antes de operar. Los valores operativos de PIN y contraseña se conservan en el archivo privado indicado por [AGENTS.md](../../AGENTS.md#credenciales-y-recursos-privados).

Nota de publicación del 2026-10-20: los identificadores de red y nodos se sustituyen por etiquetas en la versión pública; los valores originales se conservan en `local/red.md` y en el respaldo privado del historial.

## BlueOS, GPS y compases

- Por Wi-Fi `KAME`, BlueOS respondió HTTP 200 en `192.168.42.1`; el contador de `HEARTBEAT` avanzó de 973 a 975 en dos segundos. El autopiloto estaba desarmado. En otra lectura, `GPS_RAW_INT` dio fix 3D y 12 satélites.
- ArduPilot Manager mostró el GPS u-blox en el puerto D, enlace `/dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_GNSS_receiver-if00` → `/dev/ttyACM0`. Se escribieron `GPS1_TYPE=5` (NMEA) y `SERIAL2_PROTOCOL=5` (GPS), confirmados por `PARAM_VALUE`. Con autorización del usuario se solicitó reiniciar **solo** el autopiloto; la petición HTTP agotó el tiempo de espera y después volvió el heartbeat. El GPS entregó fix 3D, 12 satélites y coordenadas recibidas; permaneció desarmado.
- Siete lecturas MAVLink durante unos 30 s mantuvieron fix 3D y 12 satélites, con `GPS_RAW_INT` a ~5,5 Hz y posición variable solo unos decímetros. Tres peticiones posteriores expiraron cuando el PC perdió sus enlaces Wi-Fi y Ethernet; no se pudo distinguir una pérdida de telemetría de una pérdida de conexión del PC.
- Cockpit mostró un aviso truncado `PreArm: Compass order change requires reb...`; en otra observación figuró `PreArm: Compass calibrated requires reboot`. Más temprano se había visto `PreArm: Check mag field (xy diff: 111>100)`. No se debe inferir que todos persistan, pero sí revisar el texto completo y la calibración antes de operar.
- Por ZeroTier/4G, BlueOS y MAVLink respondieron en `10.133.182.55`; Navigator64 estaba desarmado (`base_mode=9`) y GPS informó DGPS, 12 satélites y coordenadas válidas. Los parámetros leídos a las 16:20 UTC fueron `COMPASS_USE=1`, `COMPASS_USE2=1`, `COMPASS_USE3=0`; `COMPASS_PRIO1_ID=1245450`, `COMPASS_PRIO2_ID=1379337`, `COMPASS_PRIO3_ID=0`; `COMPASS_DEV_ID=1245450`, `COMPASS_DEV_ID2=1379337`, `COMPASS_DEV_ID3=0`. MMC5983 era primario y AK09915 secundario. No se calibraron compases en esa lectura; el último `STATUSTEXT` informaba muestreo rápido del IMU, sin validar calibración.

## YOLO a 8 FPS y vídeo por distintos enlaces

- Antes del cambio, el proceso YOLO seguía activo pero había dejado de actualizar inferencias; `/cam` estaba vivo y `/yolo` repetía una imagen antigua. Sin publicación RTSP, 320 px dio 9,79 inferencias/s con un núcleo y 640 px dio 3,32/s con dos. Se mantuvo NCNN FP16 a 320 px y clases `person`/`boat`.
- Se instaló `yolo_stream.py` con objetivo de 8 inferencias/s y H.264 960×540/8 FPS. Las cajas perdidas se mantienen hasta dos inferencias (`hold` gris); hay aviso de vídeo obsoleto y watchdog para bloqueos. Se revisaron compilación, unidad systemd, lógica del arrastre y lectura de cinco frames antes de instalar. Solo se reinició `kame-yolo-detect.service`.
- La prueba posterior de `/yolo` recibió 249 frames en 30,07 s sin errores. Tras más de siete minutos, el detector seguía `active`, `NRestarts=0`, con ~7,4–7,7 inferencias/s y ~7,5–7,7 FPS. Con Cockpit reproduciendo vídeo se midieron 59,8 °C y `get_throttled=0x0`. En la vista **Boat default / Map view** del usuario JLOUREDA se vieron entonces dos vídeos y un rótulo `person 0.15`; no había objetivo conocido para confirmar que fuera un acierto.
- Los dos MediaMTX se cambiaron de escucha exclusiva en `192.168.2.2` a `0.0.0.0:8554` y `0.0.0.0:8556`. El detector pasó a leer y publicar por `127.0.0.1`. Se recargó systemd y se reiniciaron únicamente los tres servicios de cámara. Con Ethernet desconectado, ambas URL RTSP de ZeroTier devolvieron `200 OK`, SDP H.264 y más de 150 kB de RTP cada una. En la Pi se decodificó un frame de `/cam` (1920×1080) y uno de `/yolo` (960×540). Las dos fuentes aún estaban anunciadas en esa etapa.
- Se observó retraso acumulado del detector: con `CPUQuota=100%`, cgroup marcó 10.164 periodos limitados de 11.317. Se elevó **solo** `kame-yolo-detect.service` a `CPUQuota=150%` y se añadió reconexión si la lectura acumula más de 1,5 s de retraso. Después se observaron ~19,9–20,1 frames/s de decodificación de cámara y ~7,9–8,0 inferencias/FPS de salida durante más de un minuto, sin crecimiento de cola; `NRestarts=0`, 55,4 °C y `get_throttled=0x0`.
- El Wi-Fi `KAME` mostró retraso adicional: 4/10 pings del PC a la Pi perdidos, máximo 624 ms de los recibidos; una lectura inversa tuvo respuestas de ~2–7,6 s pese a 89 % de señal. No se modificó la red.
- Por último, BlueOS Video Streams pasó a anunciar **solo** `YOLO26n Person + Boat`. Se retiró el Redirect de la cámara original, pero `/cam` siguió activo para YOLO y acceso RTSP directo. Los usuarios `jloureda` y `null` quedaron con un `VideoPlayer` por vista en ROV/Boat/MAV, asociado a `Stream 1 → YOLO`; en **Boat default / Map view** se conservó el reproductor grande. En ambos usuarios se dejó `cockpit-allowed-stream-ips = []` y `cockpit-enable-auto-ice-ip-fetch = false` para que WebRTC pruebe las rutas disponibles.
- Después de ese cambio, el PC decodificó por ZeroTier 252 frames de `/yolo` en 30,12 s, 960×540, sin fallos y sin pausas mayores de 0,266 s; la imagen capturada correspondía a la escena actual. BlueOS/Cockpit respondieron HTTP 200 y la señalización WebRTC aceptó TCP en 6021. **Quedó pendiente la reproducción visual dentro del navegador Cockpit.**

Respaldos en la Pi: `/opt/kame-yolo/yolo_stream.py.bak-20261016-pre8fps`, `/etc/systemd/system/kame-yolo-detect.service.bak-20261016-pre8fps`, `/opt/kame-camera/mediamtx.yml.bak-20261016-multinet`, `/opt/kame-yolo/mediamtx.yml.bak-20261016-multinet`, `/etc/systemd/system/kame-yolo-detect.service.bak-20261016-multinet`, `/opt/kame-yolo/yolo_stream.py.bak-20261016-prelagdiag`, `/etc/systemd/system/kame-yolo-detect.service.bak-20261016-prelagfix`, `/home/pi/cockpit-video-before-yolo-only-20261016-171853.json` y `/home/pi/cockpit-ice-before-4g-20261016-172621.json`.

## Módem 4G y ZeroTier

- La Pi detectó el Luat Air780EG USB (`19d1:0001`, BYD EigenComm Compo) como `eth1` en `192.168.10.2/24`, gateway `192.168.10.1`; el puerto AT era `/dev/ttyACM1`, distinto del GPS en `/dev/ttyACM0`. Tras trasladar el módem, `AT+CPIN?` mostró `SIM PIN`. Se introdujo el PIN una sola vez y después `AT+CPIN?` devolvió `READY`. El PIN queda solo en `/etc/kame/air780eg-pin` con permisos `0600` bajo `/etc/kame` `0700`.
- Con la SIM lista, la Pi resolvió `example.com`; `curl` forzado a `eth1` obtuvo HTTPS 200 y dos pings a `1.1.1.1` respondieron en 43,7 y 64,2 ms. Se instaló `kame-air780eg-unlock.timer` y servicio: consulta antes de enviar PIN y detiene repeticiones ante intento no confirmado. La primera ejecución informó `Air780EG SIM ready`; **no se probó un ciclo físico de desconexión/reconexión**.
- ZeroTier One 1.16.2 quedó instalado en Windows y la extensión `williangalvani.zerotier` v1.14.3 en BlueOS. Red privada `ID_ZEROTIER_PRIVADO`; nodo PC `NODO_PC_PRIVADO` (`10.133.182.131`), nodo Pi `NODO_PI_PRIVADO` (`10.133.182.55`). Ambos fueron autorizados. `zerotier-local.conf` excluyó `192.168.2.0/24` y `eth0` para favorecer la salida móvil.
- Con Ethernet desconectado, la Pi mostró `eth0 NO-CARRIER` y ruta a Internet por `eth1`; ZeroTier indicó red `OK`, par en `RELAY`. BlueOS respondió HTTP 200 tres veces en 0,355–0,493 s y SSH funcionó por `10.133.182.55`. Cockpit respondió HTTP 200 en el puerto publicado 32768 de aquella sesión, que puede cambiar.

### Medidas cortas de red

| Medida | Resultado del 2026-10-16 |
| --- | --- |
| Pi → Internet por `eth1` | 30/30 pings a `1.1.1.1`; media 49 ms, rango 42–69 ms. |
| PC → Pi por ZeroTier, sin vídeo | Series 20/20 (149 ms media), 39/40 (190 ms media, pico 843 ms) y 28/30 (146 ms media). |
| BlueOS por ZeroTier | 10/10 HTTP 200; 0,295–0,326 s por petición desde el PC; 0,0005 s local desde la Pi. |
| Pi → PC por ZeroTier | 2 MiB en 4,06 s, ≈4,13 Mb/s. En sentido PC → Pi, 1 MiB en 8,81 s, ≈0,95 Mb/s. |
| 4G directo de la Pi | Descarga 2 MiB a 2,79 Mb/s; subida 1 MiB a 3,97 Mb/s. |
| Dos RTSP simultáneos por ZeroTier | `/cam` 3,05 Mb/s y `/yolo` 1,16 Mb/s: 4,21 Mb/s combinados. Ping medio 329 ms, pico 660 ms y 1/20 perdido. |
| Recursos Pi durante esa carga | ~48–53 % de CPU libre, 56,5 °C, `get_throttled=0x0`; servicios de cámara activos. |

Estas muestras no garantizan rendimiento sostenido. El caudal de dos vídeos estuvo cerca de la subida 4G medida y el par ZeroTier seguía en `RELAY`; no se pudo atribuir cada pérdida a un único tramo. Después se dejó un solo vídeo anunciado en Cockpit. La [guía de acceso móvil](../../software/conectividad/README.md) contiene los pasos de uso y diagnóstico.
