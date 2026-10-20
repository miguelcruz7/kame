# 2026-10-13 · Conectividad, Cockpit y GPS

Registro histórico. Se observó una caída de red y un arranque abrupto, pero **no quedó establecida la causa raíz**. Los estados de GPS y vídeo de este día fueron sustituidos por lecturas posteriores; ver [estado observado](../estado.md).

## Caídas de enlace

- En la primera incidencia, el PC tenía Ethernet activo a 100 Mb/s e IP `192.168.2.126/24`. `192.168.2.2` dejó de responder y luego recuperó ping, SSH y HTTP; los puertos 8554/8556 volvieron a abrir.
- El journal del arranque anterior registró `eth0 Link Down` a las 10:40:41, 10:40:50 y 10:41:00, con recuperaciones a las 10:40:48, 10:40:57 y 10:41:13. Consta un boot siguiente a las 10:42. No se halló cierre ordenado ni mensajes de OOM, kernel panic o undervoltage que explicasen el reinicio.
- Poco después hubo otra pérdida. El PC mostró Ethernet `Disconnected` (0 bps), sin ping ni TCP 22/80/8554/8556. El usuario vio luces de la Pi encendidas, pero sin LED de enlace Ethernet ni Wi-Fi de BlueOS. Un cable nuevo tampoco estableció enlace ni al PC ni al router.
- El usuario hizo un apagado/encendido forzado y la Pi recuperó acceso. El uptime consultado era de unos 4 min. Los relojes de journal y Docker no cuadraban del todo; journald detectó un archivo corrupto o sin cierre limpio. No se encontró OOM, panic o undervoltage en los registros de kernel revisados.
- En el nuevo arranque `kame-yolo-mediamtx` reintentó diez veces porque `192.168.2.2` aún no estaba asignada a `eth0`; el detector tampoco podía leer `/cam` antes de que subiera la red. La publicación se recuperó. Esa carrera de inicio podía retrasar el vídeo, pero no explicaba por sí sola la desaparición del enlace físico y del Wi-Fi.

Tras la recuperación, las tres unidades de vídeo estaban activas, ambos RTSP decodificaban y BlueOS anunciaba dos fuentes. Se midieron 50,5–51 °C, unos 14 GiB disponibles y `get_throttled=0x0`; `systemctl --failed` estaba vacío. No se modificaron servicios, configuración ni parámetros en las revisiones de diagnóstico. Si vuelve a ocurrir, observar PSU/LEDs y capturar pantalla por HDMI o consola serie mientras falla; después guardar uptime, `last -x`, journal del boot anterior, temperatura, throttling y eventos de kernel.

## Observación al abrir Cockpit

El contenedor de Cockpit atendió `GET /` y `/register_service` con HTTP 200. Permaneció `running`, `RestartCount=0`, `OOMKilled=false`. Durante 5 min 49 s se tomaron 30 muestras (11:18:08–11:23:57 del reloj de la Pi): `eth0` siguió `UP` en `192.168.2.2/24`; las tres unidades de vídeo estuvieron activas; temperatura 56,0–58,7 °C, `throttled=0x0`, unos 14 GiB disponibles, proceso YOLO 56,7–57,0 % de un núcleo y ~460–468 MB RSS. `docker stats` de Cockpit marcó 0,00 % CPU y 2,734 MiB en esas muestras. No hubo eventos de kernel/alerta.

Una muestra de `top` dio load average 6,99/5,80/4,19; `mtxrpicam` consumía ~70,6 % de un núcleo, YOLO ~52,9 %, MAVLink Camera Manager y ArduPilot ~17,6 % cada uno, y cada MediaMTX ~5,9 %. Dos lecturas de `vmstat` mostraron 54–57 % idle, 1–2 tareas ejecutables, ninguna bloqueada y sin swap. Abrir Cockpit coincidió con un periodo estable; estas muestras no establecen causalidad respecto a las caídas. Registro completo: [`cockpit-live-observation-2026-10-13.txt`](../../yolo-cockpit/diagnostics/cockpit-live-observation-2026-10-13.txt).

## GPS y evaluación del detector

- A las 11:38, `GPS_RAW_INT` llegaba fresco a ~1,53 Hz pero informó `GPS_FIX_TYPE_NO_GPS`, 0 satélites, `eph`/`epv` 65535 y coordenadas cero. Ocho lecturas adicionales entre 11:41:19 y 11:41:54 mantuvieron `NO_GPS` y 0 satélites. El enlace MAVLink sí respondía; no había posición utilizable entonces. Se detuvo la observación a petición del usuario sin cambiar parámetros.
- El detector usaba YOLO26n COCO exportado a NCNN FP16, entrada 320, clases `person` y `boat`, `conf=0.15`, límite de 2 inferencias/s y salida a 5 FPS que repetía anotaciones. Era una configuración ligera para la Pi, pero no se había validado con objetivos conocidos ni medido precisión, recall o falsas alarmas. Podía omitir objetos pequeños, lejanos o breves.

Las pruebas posteriores de GPS y detector del 2026-10-16 están en [el registro siguiente](2026-10-16-integracion.md).
