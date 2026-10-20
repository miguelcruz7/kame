# Orientación del Navigator antes de recalibrar, 2026-10-19

Horas aproximadas en CEST (UTC+2). Inspección de solo lectura por Wi-Fi `KAME`, BlueOS `http://192.168.42.1/` y MAVLink2REST `http://192.168.42.1:6040/v1/mavlink`. **El usuario hizo los cambios de parámetros y los reinicios desde BlueOS**; el asistente leyó parámetros y telemetría. Los heartbeat verificados indicaron desarmado y el asistente no envió órdenes de motor.

## Montaje físico y objetivo

El usuario confirmó que el Navigator está con la cara superior hacia arriba, la flecha `FRONT` hacia proa y la Raspberry/Navigator inclinada unos **10–13° proa abajo** respecto al plano del casco cuando este está en su posición normal de navegación. La lectura de `AHRS2.pitch` cercana a −13° con `AHRS_ORIENTATION=0` era coherente con ese montaje. El ángulo físico comunicado es aproximado: el valor −13° se usó como punto inicial y se comprobó por la actitud resultante, no con una medida mecánica de precisión.

Blue Robotics indica `None` como orientación de partida para el Navigator con cara superior arriba y flecha hacia delante. ArduPilot exige expresar la orientación de montaje antes de calibrar el acelerómetro. La inclinación fija de más de 10° no se abordó mediante `Calibrate Level`/`AHRS_TRIM_Y`, cuyo rango es ±0,1745 rad (≈±10°); se usó `Custom 1`.

## Secuencia y lecturas

| Momento | Configuración o acción del usuario | Lectura verificada por Wi-Fi |
| --- | --- | --- |
| Antes de ~18:34 | `AHRS_ORIENTATION` había sido `8` (`Roll180`), pese al montaje con cara superior arriba. El usuario lo cambió a `0` y reinició. | Con el casco quieto y derecho, `AHRS2.roll≈+1,1°`, `pitch≈−13,2°`; `ATTITUDE.roll≈−178,8°`, `pitch≈+14,2°`. El EKF/actitud principal discrepaba casi 180° en roll. No se estableció la causa. |
| ~18:55, tras otro reinicio hecho por el usuario | `AHRS_ORIENTATION=0`, `CUST_ROT_ENABLE=1`, `CUST_ROT1_PITCH=-13`, `CUST_ROT1_ROLL=0`, `CUST_ROT1_YAW=0`, `AHRS_TRIM_Y=0`. La rotación Custom 1 estaba definida, pero aún no seleccionada. | Cuatro muestras frescas: `ATTITUDE.roll≈−0,76°`, `pitch≈−13,50°`; `AHRS2.roll≈−0,88°`, `pitch≈−13,5°`. Ambas estimaciones ya coincidían en roll. El barco estaba desarmado (`HEARTBEAT.base_mode=65`). El GPS aún daba fix 3D con 12 satélites; persistía `PreArm: Compasses inconsistent`. |
| ~19:02–19:04, tras seleccionar Custom 1 y reiniciar ArduPilot | `AHRS_ORIENTATION=101` (`Custom 1`), `CUST_ROT_ENABLE=1`, `CUST_ROT1_PITCH=-13`, `CUST_ROT1_ROLL=0`, `CUST_ROT1_YAW=0`, `AHRS_TRIM_Y=0`. Todos se releyeron mediante `PARAM_REQUEST_READ`. | Cinco muestras con `ATTITUDE.time_boot_ms` creciente: `ATTITUDE.roll≈−0,68°`, `pitch≈+0,09°`; `AHRS2.roll≈−0,67°`, `pitch≈+0,10°`. El barco seguía desarmado. La corrección de montaje sí quedó aplicada y ambas actitudes coincidían mientras el casco estaba derecho y quieto. |

El valor `101` es el **código de la opción Custom 1**, no un ángulo. Los −13° residen en `CUST_ROT1_PITCH`. En BlueOS, la casilla `Custom` del editor sirve para escribir un valor numérico si el desplegable no ofrece `Custom 1`; tampoco representa por sí misma el ángulo de montaje.

## Pendiente antes de operar

- **Aún no se ha hecho ni validado una nueva calibración de acelerómetros de seis posiciones con `AHRS_ORIENTATION=101`.** Se recomienda repetirla porque las calibraciones anteriores preceden a la orientación de montaje actual. La lectura estática cercana a cero no certifica por sí sola la calibración de sesgo/escala ni la respuesta a giros. Tras calibrar, verificar roll y pitch en posición normal y al inclinar controladamente el casco.
- Tras el último reinicio, `GPS_RAW_INT` pasó a `NO_GPS`/`NO_FIX`, 0 satélites. Aparecieron `EKF3 waiting for GPS config data` y sondeo u-blox a 230400 baudios. La marca de tiempo GPS avanzó posteriormente, pero no se observó fix durante esta comprobación. Los parámetros releídos seguían en `GPS1_TYPE=2`, `GPS_AUTO_CONFIG=1`, `GPS1_RATE_MS=200`, `SERIAL2_PROTOCOL=5`. El GPS había tenido fix 3D antes del reinicio. La calibración del acelerómetro no exige fix GPS, pero la navegación y su validación sí requieren recuperarlo.
- Persistió `PreArm: Compasses inconsistent`. La corrección de pitch del Navigator no demuestra que las brújulas estén bien calibradas. Mantener el Kame desarmado y fuera de operación hasta resolver GPS, brújulas y comprobaciones prearm.
- No se verificó el archivo de respaldo de parámetros descargado desde BlueOS; solo se indicó al usuario que guardara una copia antes de editar.

## Revisión posterior con el casco en posición normal, ~19:31 CEST

Tras una interrupción del enlace Wi-Fi, el PC volvió a `KAME` (`192.168.42.10`). Seis lecturas frescas con `ATTITUDE.time_boot_ms` creciente mostraron `ATTITUDE.roll≈−0,46°`, `pitch≈+0,13°`; `AHRS2.roll≈−0,49°`, `pitch≈+0,14°`. `GPS_RAW_INT` había recuperado `DGPS`, 15 satélites y tiempo GPS creciente. No se comparó la posición con una referencia externa.

**Incidente de seguridad:** durante esas muestras `HEARTBEAT.base_mode` pasó de 65 (desarmado) a 193 (armado), y `STATUSTEXT` comunicó `Throttle armed`. Se avisó al usuario inmediatamente para que detuviera los giros, no iniciara la calibración y desarmara. A continuación, diez heartbeat consecutivos volvieron a `base_mode=65` con tiempo de arranque creciente. No se identificó quién inició el armado ni se comprobó si los motores tenían alimentación. No se enviaron comandos de armar, desarmar ni motor desde esta inspección. Antes de calibrar, asegurar el aislamiento de motores y que no se repita el armado.

## Referencias

- [Blue Robotics: Navigator Software Setup](https://bluerobotics.com/learn/navigator-software-setup/) — orientación normal y calibración de sensores.
- [ArduPilot Rover: Mounting the Autopilot](https://ardupilot.org/rover/docs/common-mounting-the-flight-controller.html) — signo del pitch de montaje y orden respecto a la calibración del acelerómetro.
- [ArduPilot Rover 4.6: parámetros](https://ardupilot.org/rover/docs/parameters-Rover-stable-V4.6.0.html) — `AHRS_ORIENTATION=101`, `CUST_ROT_ENABLE`, `CUST_ROT1_PITCH` y rango de `AHRS_TRIM_Y`.
- [Blue Robotics: AHRS Orientation settings](https://discuss.bluerobotics.com/t/ahrs-orientation-settings/19398/4) — significado de `Custom` en el editor BlueOS.
