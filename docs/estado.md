# Estado actual y siguientes tareas

**Fase actual: 1 — preparación y validación del barco.** Permanece abierta por la respuesta física de motores y las comprobaciones de vídeo y conexión automática 4G. Los objetivos y criterios de avance están en el [plan](plan.md).

**Actualización comunicada por el usuario el 2026-10-20, Europe/Madrid.** El usuario confirma armado posible, GPS correcto, ausencia de errores de brújula y calibración de acelerómetros completada con la orientación actual. Esta actualización no incluye una consulta nueva del asistente al vehículo. La fuente y el alcance están en el [registro de estado operativo](historial/2026-10-20-estado-operativo.md).

## Síntesis vigente

| Área | Estado | Fuente y alcance |
| --- | --- | --- |
| Armado | El barco puede armarse. | Confirmado por el usuario el 2026-10-20. No significa que esté armado ahora ni acredita giro de los motores. |
| GPS | Funciona correctamente. | Confirmado por el usuario. No se aportaron nuevas cifras de fix, satélites, precisión o tasa. |
| Brújula | No da errores; AK09915 restante después de desconectar MMC5983. | Confirmación actual y [comunicación del montaje](historial/2026-10-20-brujula-mmc5983.md). No se han releído prioridades ni parámetros. |
| Acelerómetros | Calibración completada con la orientación actual. | Confirmado por el usuario al preguntar por la calibración con Custom 1. No se recibieron nuevos valores ni registros de calibración. |
| Propulsión | Respuesta física de ambos motores sin comprobar. | El usuario confirmó que todavía no ha comprobado ambos lados bajo mando. |
| Vídeo Wi-Fi / 4G | Pendiente de verificar dentro de Cockpit por ambos enlaces. | Ningún ensayo nuevo de reproducción registrado. |
| Arranque 4G | Pendiente de demostrar conexión automática al encender con el módem conectado. | El temporizador de SIM por sí solo no demuestra acceso remoto completo. |

## Próximas tareas

Todas están pendientes; se preparan y registran por separado. Los ensayos se realizan con el barco desarmado y los encendidos físicos supervisados.

| Orden / ID | Tarea y procedimiento | Criterio de aceptación |
| --- | --- | --- |
| 1 — F1-VIDEO-WIFI | [Vídeo por Wi-Fi KAME](../software/video/README.md#ensayo-por-wi-fi-kame). | 60 s de imagen actual en Cockpit, movimientos conocidos en la escena, reproducción continua y sin errores. Registrar pausas y retraso observado. |
| 2 — F1-ARRANQUE-4G | [Conexión automática al encender](../software/conectividad/README.md#ensayo-de-arranque-4g). | Dos encendidos consecutivos con módem conectado y sin otra salida a Internet en la Pi. En cada intento, acceso remoto completo en un máximo inicial de 5 min, sin intervención manual de software. Registrar tiempos reales. |
| 3 — F1-VIDEO-4G | [Vídeo por 4G](../software/video/README.md#ensayo-por-4g), tras confirmar la ruta móvil. | Repetir los 60 s y movimientos conocidos dentro de Cockpit desde un PC con Internet independiente. RTSP o procesos activos no bastan. |
| 4 — F1-MOTORES | [Comprobar respuesta por lado](preparacion.md#5-propulsión-y-control-manual). | Procedimiento específico autorizado y supervisado, respuesta física observada en cada lado y estado final registrado. La capacidad de armar no cierra esta tarea. |

Para F1-ARRANQUE-4G se comprueban SIM, interfaz móvil, ruta por el módem y ZeroTier; deben funcionar BlueOS, SSH y heartbeat fresco por ZeroTier. El AP KAME puede permanecer activo. Si hay que conectar manualmente o reiniciar un servicio, ese intento no cumple. Un intento de PIN sin confirmar se registra y revisa antes de repetirlo.

Cada resultado indicará fecha/zona horaria, fuente, enlace, condiciones, evidencia y estado final. Si falla vídeo o arranque, abrir una tarea de diagnóstico concreta antes de proponer cambios de configuración. Las condiciones generales están en [preparación](preparacion.md).

## Última inspección directa del asistente

La última lectura directa del vehículo fue el **2026-10-19 ~19:53 CEST**, por Wi-Fi KAME. Tras las pruebas PWM autorizadas, heartbeat desarmado y salidas 1/2 a 1500 µs; no se observó giro. El último intento de enlace de esa sesión, a las ~20:07, falló. Son observaciones históricas; no describen la conectividad actual tras la actualización del usuario.

Los registros conservan el [diagnóstico de motores](historial/2026-10-19-motores-esc.md), [GPS y telemetría](historial/2026-10-19-gps.md) y [orientación](historial/2026-10-19-orientacion-navigator.md). No se repitieron pruebas ni se cambiaron parámetros durante esta actualización documental.

## Antecedentes y trabajo posterior

- Las caídas de telemetría/enlace y el armado transitorio anteriores conservan causa sin determinar. No hay evidencia nueva que los sitúe como fallos presentes ni que permita cerrar su causa. Revisar su disposición antes de ampliar los ensayos según el plan.
- La calibración que figuraba pendiente quedó sustituida por la confirmación del usuario de que está completada. Las futuras sesiones mantienen las comprobaciones previas normales.
- La diferencia entre GPS interno/registrado a ~5 Hz y GPS_RAW_INT a ~2 Hz en MAVLink2REST queda como análisis posterior.
- La evaluación de YOLO con escenas conocidas y falsas alarmas sigue pendiente antes de utilizarlo para evasión.
- También quedan la frescura independiente de GPS/armado en el visor, la procedencia y recuperación externa de recursos, y la elección de licencia y revisión de licencias de dependencias. El repositorio se publica en [GitHub](https://github.com/miguelcruz7/kame), según su [registro de publicación](historial/2026-10-20-publicacion-github.md).

El [historial](historial/README.md) conserva la evidencia y las actualizaciones anteriores.
