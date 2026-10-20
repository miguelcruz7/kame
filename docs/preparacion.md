# Preparación y ensayos del barco

Guía de procedimientos para la puesta en servicio y las sesiones de prueba. Consultar [AGENTS.md](../AGENTS.md), el [estado vigente](estado.md) y el [inventario de hardware](hardware.md). Los procedimientos no marcan por sí solos una tarea como completada.

## 1. Inventario y respaldo

Identificar placa, ordenador de a bordo, alimentación, sensores, comunicaciones, ESC y motor por lado. Confirmar cableado, masas, pines y compatibilidad de alimentación. Registrar modelo, fuente y lo que no se pudo comprobar.

Guardar parámetros, configuración de BlueOS, asignaciones de puertos y versiones antes de modificar. Los [snapshots existentes](historial/parametros/README.md) son lecturas históricas, no una configuración aprobada para restaurar automáticamente. Conservar ubicación, hash y alcance de recuperación de cada respaldo.

## 2. BlueOS y firmware

Leer versiones y selección de placa y contrastarlas con hardware y documentación oficial aplicable. Para instalar o actualizar, confirmar compatibilidad, guardar configuración y acordar recuperación.

Firmware, placa/puerto y reinicios requieren autorización y condiciones de seguridad verificadas. Registrar origen, versión, plataforma y hash del archivo. Leer después el estado: una interfaz web disponible no demuestra heartbeat fresco de ArduPilot.

## 3. Inspección y enlaces

Elegir un enlace de la [tabla de redes](hardware.md#red-y-puertos). Empezar con consultas de solo lectura y registrar fecha, enlace, fuente y límites:

1. Confirmar heartbeat que avanza y estado de armado actual. Poder armar no significa estar armado ni valida la respuesta de los motores.
2. Leer GPS_RAW_INT: fix, satélites y coordenadas; contrastar la posición con el lugar físico.
3. Revisar avisos prearm/brújula y la respuesta de actitud/rumbo.
4. Comprobar cámara y vídeo según el enlace y el procedimiento de Cockpit.

Priorizar API documentada de la versión instalada de BlueOS, MAVLink/MAVLink2REST o SSH. Usar la interfaz cuando aporte evidencia visual o una función sin API fiable. Comprobar frescura de cada dato; HTTP 200 no acredita telemetría ni la caché acredita estado presente.

Si desaparece ArduPilot, recoger procesos y registros antes de atribuir causa. Evitar lectores competidores en el puerto GPS que usa ArduPilot y verificar la identidad del dispositivo antes de abrir un puerto. El [registro GPS](historial/2026-10-19-gps.md) conserva el análisis anterior.

## 4. Montaje y calibración

Consultar el montaje documentado en [hardware](hardware.md#navigator-montaje-y-calibración). Expresar la orientación de montaje antes de realizar una calibración. Si cambia el montaje o se necesita recalibrar, seguir el procedimiento oficial correspondiente y registrar el resultado.

Con motores aislados y vehículo desarmado, comprobar actitud, respuesta al movimiento, rumbo e interferencias de alimentación/propulsión. Utilizar la brújula indicada por el inventario vigente; no restaurar la selección de sensores de snapshots anteriores sin revisar el montaje.

El prearm saludable y la ausencia de errores son observaciones distintas de un registro de calibración. Consultar en [estado](estado.md) qué se ha confirmado ya y no reabrir una calibración completada únicamente porque siga apareciendo como pendiente en una entrada histórica. Las [fuentes de orientación](historial/2026-10-19-orientacion-navigator.md) conservan la secuencia anterior.

## 5. Propulsión y control manual

Preparar la tarea de ensayo indicando los equipos por lado, su conexión real, alimentación de potencia, señal, masa e indicaciones del ESC. Verificar destino y compatibilidad de cualquier BEC. El [registro de motores](historial/2026-10-19-motores-esc.md) conserva detalles y fuentes del montaje comunicado.

Un PWM reportado confirma lo ordenado, no la señal eléctrica ni el giro. Las pruebas requieren autorización explícita, supervisión junto al barco, disposición segura de hélices y corte accesible. Respetar los límites del fabricante y no prolongar pruebas en seco.

Comprobar cada lado, sentido, neutral y respuesta mediante el procedimiento acordado; después mando manual, parada y recuperación. Registrar observación física y estado final. La capacidad de armar no sustituye esta comprobación.

## 6. Vídeo y acceso remoto

Preparar los ensayos como tareas independientes y realizarlos con el barco desarmado. Cada encendido físico debe estar supervisado. El orden de trabajo y su resultado se mantienen en [estado](estado.md).

1. [Vídeo por Wi-Fi KAME](../software/video/README.md#ensayo-por-wi-fi-kame): 60 s en Cockpit con movimientos conocidos de la escena.
2. [Arranque automático por 4G](../software/conectividad/README.md#ensayo-de-arranque-4g): dos encendidos consecutivos, módem conectado y sin salida a Internet alternativa en la Pi; máximo inicial de 5 min por intento.
3. [Vídeo por 4G](../software/video/README.md#ensayo-por-4g): repetir la comprobación visual una vez confirmada la ruta móvil.

Registrar tiempos, pausas, errores y retraso observado. Un servicio activo, RTSP decodificable o señalización WebRTC no acreditan por sí solos imagen actual en Cockpit. Si un ensayo falla, registrar su diagnóstico antes de proponer una intervención.

Las precauciones del desbloqueo SIM, incluidos intentos de PIN sin confirmar, están en la [guía de conectividad](../software/conectividad/README.md).

## 7. Cierre y registro

Revisar los criterios de fase del [plan](plan.md), asociando evidencia y límites. Mantener configuración aprobada por separado de los snapshots. Ensayar cambios de navegación en SITL antes de las pruebas reales acordadas.

Cada sesión registra ID, objetivo, fecha/zona horaria, entorno y enlace, versión/configuración, autorización, resultado, métricas, evidencias recuperables y estado final. Conservar DataFlash, tlog, vídeo y detecciones bajo el mismo ID cuando existan. Los archivos pesados van en `local/registros/<ID>/`; sus ubicaciones y hashes se anotan en la entrada fechada del historial.
