# Diagnóstico inicial de motores y ESC — 2026-10-19

Inspección de solo lectura por Wi-Fi `KAME` (`http://192.168.42.1/`) entre las 19:33 y las 19:37 CEST. Fuente: API MAVLink2REST de BlueOS (`/mavlink2rest/v1/mavlink/vehicles/1/components/1/messages`) y respuestas a `PARAM_REQUEST_READ`. No se armó, accionó motores, modificaron parámetros ni reinició el sistema durante esta inspección.

| Lectura | Resultado | Límite |
| --- | --- | --- |
| `HEARTBEAT` | Dos lecturas a las 19:35:03 y 19:35:05, contadores 503 y 505, `base_mode=65` (desarmado). | A las ~19:31 hubo un armado transitorio de origen desconocido; el estado actual debe volver a comprobarse antes de intervenir. |
| `GPS_RAW_INT` | Dos mensajes frescos, `DGPS`, 17 satélites, latitud bruta `433382097` y `433382093`, longitud bruta `-83780329` en ambos. | No se cotejó la posición con una referencia física. |
| `SERVO_OUTPUT_RAW` | Contadores 1391 y 1395; salidas 1 y 2 en 1500 µs, con el vehículo desarmado. | Es el valor reportado por ArduPilot; no mide la señal en los pines ni demuestra que los ESC estén alimentados. |
| Parámetros actuales | `FRAME_CLASS=2`, `SERVO1_FUNCTION=73`, `SERVO2_FUNCTION=74`, `SERVO3_FUNCTION=0`, `MOT_PWM_TYPE=0`; salidas 1 y 2: `MIN=1100`, `MAX=1900`, `TRIM=1500`, `REVERSED=0`. | `SERVO2_FUNCTION` era 0 en la lectura de las 17:45–17:47. Se desconoce cuándo o quién lo cambió a 74. |
| Telemetría ESC | No había mensajes con nombre `ESC*` en el conjunto de mensajes MAVLink2REST consultado. | Un ESC conectado solo mediante PWM no se identifica por ese enlace; la ausencia de telemetría no demuestra que esté ausente o averiado. |
| `STATUSTEXT` | El último mensaje almacenado era `Throttle disarmed` a las 19:31:18. | No representa una comprobación actual de los avisos prearm; el último aviso de brújulas inconsistentes documentado es anterior. |
| Entrada y batería, ~19:37 | `RC_CHANNELS` fresco informó `chancount=0` y canales 1–18 en 0; `VFR_HUD.throttle=0`; `BATTERY_STATUS` informó 15,133 V. | No se movió un joystick durante esta lectura. Cockpit puede enviar `MANUAL_CONTROL` sin aparecer como canales RC; esta observación no demuestra un fallo de mando. La tensión de batería que conoce ArduPilot no verifica la alimentación de cada ESC. |

El usuario informó de un propulsor Blue Robotics T200 y un ESC marino Spektrum SPMXME1A de 100 A para LiPo 3–4S, alimentación desde batería 4S, y mencionó que el equipo Blue Robotics está a la derecha. Confirmó que el lado derecho está conectado a la salida PWM 2 del Navigator. No quedó establecido el modelo de cada ESC y cada motor por lado ni si el lado izquierdo está realmente conectado a PWM 1. El usuario informó que el barco está sujeto y fuera del agua; no confirmó que las hélices estén retiradas. No se realizó prueba de giro.

Antes de atribuir la falta de giro a la configuración, verificar físicamente la alimentación de potencia de cada ESC, su indicación de arranque, señal y masa en el conector correcto, y el cableado de motor. El Navigator entrega señal PWM de 3,3 V en los pines de salida y su raíl auxiliar no se alimenta desde la entrada principal de 5 V. El Spektrum SPMXME1A anuncia BEC de 6 V; comprobar dónde termina su cable rojo y evitar alimentar el raíl AUX 5V sin verificar compatibilidad. La comprobación de giro requiere identificar los equipos, confirmar una disposición segura de hélices y resolver las condiciones pendientes de prearm/GPS. El T200 requiere agua para lubricación; no usar un giro sostenido en seco.

## Relectura y plan de prueba, ~19:41–19:42 CEST

Por el mismo enlace y API, dos heartbeat a las 19:41:21 y 19:41:24 pasaron de contador 881 a 884 con `base_mode=65` (desarmado); una tercera lectura a las 19:42:11 también indicó desarmado. Tres `GPS_RAW_INT` frescos indicaron `DGPS`, 20 satélites y coordenadas recibidas, sin cotejo físico. `SERVO_OUTPUT_RAW` seguía informando 1500 µs en salidas 1 y 2. `STATUSTEXT` seguía almacenando `Throttle disarmed` de las 19:31:18; no se obtuvo un aviso prearm actual. No se comprobó cámara o reproducción WebRTC en Cockpit durante este diagnóstico de motores.

La documentación oficial de ArduRover indica que la función `Motor Test` **arma internamente los motores** durante la prueba y los desarma al terminar; también deshabilita temporalmente tres failsafes. Por ello no se envió un `MAV_CMD_DO_MOTOR_TEST` con el aviso anterior de brújulas sin resolver y la posición GPS sin validar. Las funciones 73/74 y el PWM neutro permiten preparar comprobaciones pasivas de alimentación, señal y masa; todavía no justifican un giro remoto.

## Estado prearm, ~19:44 CEST

Ante la pregunta del usuario sobre GPS y brújula, se releyeron dos `SYS_STATUS` frescos por Wi-Fi `KAME` a las 19:44:32 y 19:44:34 CEST. En ambos, el bit 4 (magnetómetro), el bit 32 (GPS) y el bit 268435456 (`PREARM_CHECK`) figuraron presentes, habilitados y saludables. `GPS_RAW_INT` indicó `DGPS`, 20 satélites; los heartbeat seguían en `base_mode=65` (desarmado). `ARMING_OPTIONS=0` se leyó mediante `PARAM_REQUEST_READ`. El último `STATUSTEXT` almacenado seguía siendo `Throttle disarmed` a las 19:31:18, sin otro aviso prearm posterior en esa caché. Estas señales indican que el autopiloto no está señalando el fallo previo actualmente, pero no sustituyen el cotejo de la posición GPS con el lugar físico ni la revisión de calibración individual de las brújulas.

Se intentó solicitar `MAV_CMD_RUN_PREARM_CHECKS`, que ejecuta solo las comprobaciones y no arma según la documentación de MAVLink y el controlador de ArduPilot. La API MAVLink2REST instalada rechazó el JSON antes de enviarlo (`Failed to parse message, not a valid MAVLinkMessage`); no se recibió `COMMAND_ACK` ni se efectuó esa comprobación bajo demanda. No se enviaron comandos de armado ni de motor.

## Pruebas de salida PWM autorizadas, 19:50–19:51 CEST

El usuario autorizó expresamente las pruebas, confirmó estar junto al barco, con las hélices despejadas, acceso inmediato al corte de batería y que la posición GPS mostrada corresponde al lugar físico. Antes de cada pulso se releyeron por Wi-Fi `KAME` el heartbeat desarmado (`base_mode=65`), GPS `DGPS` con 20–21 satélites, el indicador `PREARM_CHECK` saludable y ambas salidas en 1500 µs. La batería reportada por ArduPilot era de unos 15,1 V. Se usó la API MAVLink2REST de BlueOS para enviar `MAV_CMD_DO_MOTOR_TEST`, tipo de acelerador 1 (PWM directo), duración de 1 s y 1550 µs, un motor cada vez. No se cambiaron parámetros ni se reinició el sistema.

| Hora CEST | Prueba | Respuesta MAVLink y salida reportada | Estado final |
| --- | --- | --- | --- |
| 19:50:46 | Motor derecho, instancia 4, función 74 en PWM 2 | `COMMAND_ACK: MAV_RESULT_ACCEPTED`; PWM 2 pasó de 1500 a 1550 µs; PWM 1 permaneció en 1500 µs. `STATUSTEXT`: `Throttle armed`. | A las 19:50:48 heartbeat desarmado (`base_mode=65`), PWM 1 y 2 en 1500 µs; `Throttle disarmed`. |
| 19:51:06 | Motor izquierdo, instancia 3, función 73 en PWM 1 | `COMMAND_ACK: MAV_RESULT_ACCEPTED`; PWM 1 pasó de 1500 a 1550 µs; PWM 2 permaneció en 1500 µs. `STATUSTEXT`: `Throttle armed`. | A las 19:51:08 heartbeat desarmado (`base_mode=65`), PWM 1 y 2 en 1500 µs; `Throttle disarmed`. |

El `HEARTBEAT` indicó brevemente `base_mode=193` durante cada prueba, coherente con el armado interno de `Motor Test`. La telemetría demuestra que ArduPilot aceptó ambas órdenes y reportó las salidas correctas por separado; no demuestra tensión en los conectores ni giro físico de los motores. Queda pendiente la observación presencial del usuario de cada lado. No se repitieron ni alargaron los pulsos en seco.

## Repetición de 5 segundos solicitada por el usuario, 19:52 CEST

El usuario pidió expresamente repetir las dos pruebas durante 5 s cada una. Se mantuvo 1550 µs y se comprobó de nuevo antes de cada envío: heartbeat desarmado, GPS `DGPS` con 20 satélites, indicador prearm saludable y PWM 1/2 en 1500 µs. No se modificaron parámetros.

| Lado y hora CEST | Respuesta y PWM reportado | Final |
| --- | --- | --- |
| Derecho, 19:52:20–25 | `MAV_CMD_DO_MOTOR_TEST` aceptado; PWM 2 = 1550 µs, PWM 1 = 1500 µs durante unos 5 s. | `Throttle disarmed`; a las 19:52:26 heartbeat desarmado y ambos PWM en 1500 µs. |
| Izquierdo, 19:52:26–31 | Comando aceptado; PWM 1 = 1550 µs, PWM 2 = 1500 µs durante unos 5 s. | `Throttle disarmed`; a las 19:52:32 heartbeat desarmado y ambos PWM en 1500 µs. |

Cada lado acumula aproximadamente 6 s de prueba en seco en esta sesión. El usuario informó después: «no vi nada». No confirmó si hubo pitidos o indicadores luminosos en los ESC. El valor `SERVO_OUTPUT_RAW` solo confirma la salida ordenada por ArduPilot; no hay evidencia de giro físico ni de recepción de la señal por los ESC. Una lectura posterior a las 19:53:37 mostró heartbeat desarmado, ambas salidas en 1500 µs y batería reportada de 15,089 V / 0,17 A en reposo. No se registró corriente durante los pulsos.

## Solicitud de prueba directa con Navigator, ~20:07 CEST

El usuario aportó un procedimiento para detener ArduPilot y probar PWM 1 y 2 directamente mediante Navigator WebAssistant o `bluerobotics_navigator`; confirmó que las condiciones de supervisión y seguridad estaban preparadas. Antes de cambiar nada se intentó recuperar el enlace con el vehículo. El ordenador tenía Wi-Fi doméstico `192.168.0.14`, no `KAME`; el perfil `KAME` existe, pero `netsh wlan connect name=KAME` respondió que la red no estaba disponible. Un escaneo posterior tampoco mostró el SSID. BlueOS no respondió por `192.168.42.1` ni por la IP doméstica previamente observada `192.168.0.21`; SSH a `192.168.42.1`, `192.168.2.2`, `192.168.0.21` y `10.133.182.55` tampoco estuvo disponible. No se detuvo ArduPilot, no se instaló extensión, no se modificó firmware o selección de placa y no se enviaron señales PWM directas. La prueba queda pendiente de restaurar el enlace y verificar de nuevo estado desarmado y condiciones de seguridad.
