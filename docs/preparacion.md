# Preparación del barco — fase 1

Consultar antes [AGENTS.md](../AGENTS.md), [estado observado](estado.md) y [hardware](hardware.md). Los parámetros y versiones históricos son referencias; comprobar la instalación presente antes de aplicar un procedimiento.

## 1. Inventario y respaldo

Identificar placa, Raspberry, alimentación, GPS, cámara, módem, ESC y motor por lado. Confirmar cableado, masas, pines y compatibilidad de alimentación. Registrar modelo, fuente y lo pendiente de comprobar.

Guardar parámetros, configuración de BlueOS, asignaciones de puertos y versiones antes de modificar. Los [snapshots existentes](historial/parametros/README.md) son lecturas históricas, no una configuración aprobada para restaurar a ciegas. Conservar ubicación, hash y alcance de recuperación de cada respaldo.

## 2. BlueOS y firmware

La última instalación documentada era BlueOS 1.4.3 y ArduRover 4.6.3 en Navigator64. Releer versiones y selección de placa. Para instalar o actualizar, contrastar documentación oficial de la versión y hardware, confirmar compatibilidad, guardar configuración y acordar recuperación.

Firmware, placa/puerto y reinicios requieren autorización y condiciones de seguridad verificadas. Registrar origen, versión, plataforma y hash del archivo. Leer después el estado: una interfaz web disponible no demuestra heartbeat fresco de ArduPilot.

## 3. Telemetría y enlaces

Elegir un enlace de la [tabla de redes](hardware.md#red-y-puertos). Confirmar heartbeat que avanza y armado actual; después GPS, avisos prearm y sensores. Guardar fecha, enlace y fuente. No interpretar la caché de MAVLink2REST como telemetría presente.

Si desaparece ArduPilot, recoger procesos y registros antes de atribuir causa. El [registro GPS](historial/2026-10-19-gps.md) diferencia caída del autopiloto, recuperación y tasas del receptor frente a MAVLink. Evitar lectores competidores en el puerto GPS que usa ArduPilot.

## 4. Montaje y calibración

Confirmar proa, ejes y montaje. La corrección documentada del Navigator es `Custom 1`, pitch −13°, con buen acuerdo estático; falta validar una calibración completa con esa orientación. Consultar la [secuencia y fuentes de orientación](historial/2026-10-19-orientacion-navigator.md).

Con motores aislados y vehículo desarmado, seguir el procedimiento oficial de acelerómetros y comprobar la respuesta al movimiento. Verificar rumbo, calibración de brújulas e interferencias de alimentación/propulsión. El prearm saludable posterior a un aviso no certifica individualmente las calibraciones.

Validar fix, satélites y posición GPS frente al lugar físico en cada sesión de navegación. La configuración más reciente documentada usa u-blox; NMEA fue el ajuste anterior del 16 de octubre. DGPS no demuestra RTK fijo; no hay una cadena RTCM/NTRIP validada en estos registros.

## 5. Propulsión y control manual

Identificar modelo y conexión real de cada ESC/motor. Confirmar alimentación de potencia, indicaciones del ESC, señal y masa. Verificar dónde termina cualquier BEC y su compatibilidad; el [registro de motores](historial/2026-10-19-motores-esc.md) conserva detalles y fuentes del montaje comunicado.

PWM en telemetría confirma lo ordenado, no la señal eléctrica ni el giro. Las pruebas requieren autorización, supervisión junto al barco, disposición segura de hélices y corte accesible. Respetar los límites del fabricante y no prolongar pruebas en seco.

Comprobar cada lado, sentido, neutral y respuesta mediante el procedimiento acordado; después mando manual, parada y recuperación. Registrar observación física y estado final. El armado transitorio de origen desconocido y las pruebas sin giro siguen abiertos en [estado.md](estado.md).

## 6. Vídeo y acceso remoto

Leer [vídeo](../software/video/README.md) y [conectividad](../software/conectividad/README.md) antes de intervenir. Confirmar imagen actual y fluida dentro de Cockpit por el enlace de uso; procesos, RTSP y señalización son comprobaciones distintas.

Si se va a usar 4G, comprobar módem presente, SIM lista, interfaz y ruta móvil, ZeroTier online y recuperación después de un arranque en frío autorizado. El temporizador desbloquea la SIM cuando aparece el puerto; no acredita conectividad.

## 7. Cierre y registro

Revisar los criterios de fase 1 del [plan](plan.md), asociando evidencia y límites. Conservar configuración aprobada por separado de los snapshots. Empezar waypoints en SITL y después en agua protegida cuando las comprobaciones permitan ese ensayo.

Cada sesión registra ID, objetivo, fecha/zona horaria, entorno y enlace, versión/configuración, autorización, resultado, métricas, evidencias recuperables y estado final. Conservar logs DataFlash, tlog, vídeo y detecciones bajo el mismo ID cuando existan. Los archivos pesados van en `local/registros/<ID>/`; sus ubicaciones y hashes se anotan en la entrada fechada del historial.
