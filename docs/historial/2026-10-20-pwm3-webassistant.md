# PWM3: intento con Navigator WebAssistant y recuperación — 2026-10-20

**ID:** `F1-PWM3-WEBASSISTANT-20261020-210740`. Fecha/zona: 2026-10-20, Europe/Madrid. Objetivo: determinar si el Basic ESC reconoce señal y neutro desde PWM3 sin pasar por ArduPilot, únicamente al equivalente de 1500 µs y sin órdenes de giro. Corresponde a F1-MOTORES, pero no acredita respuesta física bajo mando ni navegación.

## Fuente, autorización y condiciones

El usuario confirmó en esta conversación un T200 con Basic ESC de Blue Robotics, conexión actual a PWM3 y función `Throttle Right (74)`. Según su observación, el mismo conjunto funciona conectado directamente a un receptor RC, mientras que con Navigator se escuchan únicamente tres pitidos ascendentes. No se recibió grabación ni medida eléctrica del pulso.

El usuario solicitó implementar el plan de ensayo y estar junto al barco durante las operaciones. Al preguntar por las condiciones físicas informó de que el ESC de prueba seguía alimentado. Se explicó la alternativa de mantener batería retirando del Navigator los conectores de control de los ESC durante la preparación. Ante la solicitud de confirmar ese aislamiento, a las 21:13 CEST respondió: «acabamos de desconectar el control del navigator». Se procedió únicamente a preparar el software, manteniendo el control desconectado. La extensión falló antes del ensayo; no se indicó reconectar el control ni se enviaron órdenes PWM, de armado o de giro. No se realizó una inspección visual independiente del aislamiento.

Entorno: consultas HTTP a BlueOS por ZeroTier/4G, MAVLink2REST y SSH autenticado por contraseña para lecturas de procesos y respaldo de archivos. BlueOS 1.4.3; placa seleccionada `Navigator64`, plataforma `navigator64`; firmware 4.7.2 STABLE. La referencia anterior de PWM2 y firmware 4.6.3 es histórica y no describe esta lectura. La rama y el commit exactos, con los cambios locales preexistentes, se conservan en `session.json`; no se cambiaron de rama ni se publicaron cambios.

## Lecturas y respaldo

La exportación por `PARAM_REQUEST_LIST`, recibida mediante un WebSocket filtrado a `PARAM_VALUE`, recuperó **915 de 915 parámetros**. No se enviaron `PARAM_SET`, órdenes de armado ni pruebas de motor.

| Elemento | Lectura actual |
| --- | --- |
| Funciones de salida | PWM1 = 73; PWM2 = 0; PWM3 = 74. |
| PWM3 | MIN = 1100, MAX = 1900, TRIM = 1500 µs; REVERSED = 1. |
| Generación PWM | `MOT_PWM_TYPE=0`, `SERVO_RATE=50`, `SERVO_GPIO_MASK=0`. |
| Desarmado/seguridad | `MOT_SAFE_DISARM=0`, `ARMING_REQUIRE=1`, `BRD_SAFETY_DEFLT=0`. |
| Telemetría inicial | Heartbeat desarmado; `SERVO_OUTPUT_RAW.servo3_raw=1500`. Es la orden reportada, no una medida del pin. |
| WebAssistant, antes | No instalado. Catálogo: `bluerobotics.navigator-webassistant`, versión 1.0.0. |

Evidencia privada en `local/registros/F1-PWM3-WEBASSISTANT-20261020-210740/`: exportaciones `parameters-before.json` y `.params`, placa/firmware, esquemas de las API instaladas, extensiones previas, telemetría y procesos. `ardupilot-manager-before.tar.gz` contiene `settings.json`, ejecutable original y almacenamiento del autopiloto, sin logs históricos; SHA-256 `293ced1cc9090db4d2ccb79571e53871af47b1346da2da32abbd6b5240bdbd74`. Se verificó la lectura completa de sus miembros. El almacenamiento se copió con ArduPilot funcionando y no se presenta como snapshot atómico; la exportación MAVLink completa se conserva por separado. `SHA256.json` identifica los archivos.

## Ejecución y fallo

| Hora CEST | Operación y evidencia |
| --- | --- |
| 21:13:31 | `POST /ardupilot-manager/v1.0/stop`. Después no aparecían procesos del autopiloto y dos lecturas del heartbeat conservaron el contador 1895 y la misma fecha. La interrupción de telemetría durante esta ventana fue intencionada. |
| 21:13:59 | Instalación de WebAssistant 1.0.0 mediante la API de Extensions Manager; descarga concluida e imagen identificada por digest. |
| 21:15:58 | El contenedor arrancó y terminó unos 0,37 s después con código 101. Su registro identifica `navigator-rs-0.3.0` y un pánico durante `CS2 export`: error del SO 22, `InvalidInput`, `Invalid argument`. No llegó a estar disponible la interfaz de prueba. |
| 21:16:19 | Extensión deshabilitada mediante la API; lectura posterior `enabled=false`. Contenedor no ejecutándose y sin proceso `navigator-webassistant`. |
| 21:16:24 | `POST /ardupilot-manager/v1.0/start`. Dos lecturas posteriores: heartbeat desarmado, Manual, contadores 1906 y 1908 y fechas avanzando. Placa Navigator64 y firmware 4.7.2 STABLE recuperados. |

Imagen instalada: `raulelektron/blueos-navigator-webassistant:1.0.0`, digest arm64 `sha256:f40e068095246755e3790e0dc70f462304671906dec44f3652ad1b727aa9bf4f`. Contenedor: `extension-raulelektronblueosnavigatorwebassistant100`. Queda instalado y deshabilitado; su política de reinicio Docker observada era `no`. El ejecutable original de ArduPilot conservó SHA-256 `e0cede800da4bd895ec3d60f2d4ea68879e16f6da6998716440f8dded5ed736e` antes/después.

**Resultado:** WebAssistant no pudo inicializar su biblioteca de acceso al hardware. Es compatible con una incompatibilidad de GPIO/biblioteca en esta instalación Raspberry Pi 5, pero no se aisló la causa exacta. No demuestra avería de PWM3, no mide el pulso y no prueba inicialización del ESC. No se corrigió ni sustituyó la biblioteca: queda fuera de este ensayo.

## Preparación estática que no llegó a ejecutarse

- La compatibilidad arm64 del catálogo no demuestra compatibilidad de la biblioteca con Raspberry Pi 5 ni con los sensores conectados.
- Antes de cualquier ensayo posterior, verificar las unidades en su versión efectiva. En el [código publicado](https://github.com/bluerobotics/navigator-web-assistant/blob/master/src/hardware_manager.rs), `channel/value` llega a la biblioteca como valor del contador; en navigator-rs 0.3.2 son cuentas de 0–4095. A 50 Hz, 307 cuentas equivalen aproximadamente a 1499 µs. Es un cálculo de preparación, no un valor aplicado ni una validación del binario instalado, que informó biblioteca 0.3.0.
- La [operación REST de frecuencia](https://github.com/bluerobotics/navigator-web-assistant/blob/master/src/server/protocols/v1/rest.rs) habilita PWM automáticamente. Mantener aislamiento durante arranque/configuración y deshabilitar de nuevo después de establecer 50 Hz.
- Preparar únicamente `Ch3`, reconectar la potencia o el control aislado según el método confirmado y observar hasta 10 s. El [Basic ESC](https://bluerobotics.com/learn/thruster-usage-guide/#esc-beeps) debe añadir un pitido de señal y otro de neutro a los tres de encendido. Cortar potencia ante movimiento inesperado o pérdida de enlace.
- Al terminar, cortar potencia del ESC, deshabilitar y detener la extensión, verificar su salida y recuperar ArduPilot. Contrastar parámetros con el respaldo y dejar desarmado. Si falla la extensión, no atribuir por ello avería a PWM3.

## Verificaciones finales y traspaso

La segunda exportación recuperó nuevamente 915/915 parámetros. Las funciones, límites, trim y reversión de PWM3, frecuencia, tipo de PWM y ajustes de seguridad revisados permanecieron iguales. La comparación completa encontró únicamente `COMPASS_DEC` (−0,0279379617 → −0,0279329736), `BARO1_GND_PRESS` (101877,34375 → 101658,1953125), `STAT_BOOTCNT` (37 → 38) y `STAT_RUNTIME` (36197 → 36506). No se enviaron escrituras de parámetros; las diferencias se observaron después de volver a arrancar el autopiloto. No se restauraron ciegamente valores calculados o contadores.

Evidencias adicionales bajo el mismo ID: `operations.jsonl`, `install-decoded.json`, `webassistant-start-failure.json`, `extension-disabled-details.json`, heartbeat/procesos de recuperación, `parameters-after.json`, `.params` y `parameters-comparison.json`. Las comprobaciones portátiles del repositorio verificaron documentos, enlaces, sintaxis, secretos conocidos, generación de misiones y visor; no acreditan comportamiento del vehículo.

**Ensayo del neutro bloqueado por el fallo de arranque de WebAssistant; recuperación del autopiloto verificada.** Mantener la extensión deshabilitada. El control del ESC quedó desconectado según la última comunicación del usuario; no se verificó reconexión física. El siguiente paso requiere una versión de WebAssistant/biblioteca compatible y un ensayo nuevo autorizado, o una medición independiente de la señal física. No se realizaron cambios en firmware, placa o configuración PWM para intentar resolver el fallo.
