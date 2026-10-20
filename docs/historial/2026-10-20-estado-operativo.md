# Estado operativo comunicado por el usuario — 2026-10-20

**Fuente:** comunicación directa del usuario en esta conversación, recibida el 2026-10-20, Europe/Madrid. No hubo una nueva conexión del asistente al vehículo ni una lectura de parámetros, sensores o servicios durante esta actualización.

## Confirmaciones

| Área | Información aportada |
| --- | --- |
| Armado | El barco puede armarse; no se indicó que estuviera armado en el momento de la comunicación. |
| GPS | Funciona correctamente. No se aportaron cifras nuevas de fix, satélites, precisión, posición o tasa. |
| Brújula | No da errores. Se conserva la identificación de AK09915 tras la [desconexión comunicada de MMC5983](2026-10-20-brujula-mmc5983.md). |
| Acelerómetros | Ante la pregunta por la calibración con la orientación actual Custom 1 de −13°, el usuario confirmó que está completada. No se aportaron registros ni nuevos valores de parámetros. |
| Motores | Ante la pregunta por la respuesta física de ambos motores al mando, el usuario confirmó que aún está sin comprobar. |

La calibración antes pendiente se registra como completada por confirmación del usuario. Ausencia de errores de brújula no equivale a una nueva lectura de sus prioridades ni a una medida independiente de rumbo.

## Ensayos acordados y todavía pendientes

1. Vídeo actual dentro de Cockpit por Wi-Fi KAME durante 60 s, con movimientos conocidos de la escena.
2. Conexión automática tras dos encendidos consecutivos con el módem conectado y sin Internet alternativo en la Pi: SIM, interfaz y ruta móvil, ZeroTier, BlueOS, SSH y heartbeat fresco. Máximo inicial de 5 min por intento, midiendo el tiempo real y sin intervención manual de software.
3. Vídeo por 4G, repitiendo la comprobación visual una vez validada la ruta móvil.
4. Respuesta física de ambos motores mediante una tarea específica autorizada y supervisada.

Los ensayos se preparan por separado con el barco desarmado y encendidos supervisados. En esta actualización no se ejecutó ninguno, no se armó ni se accionaron motores y no se cambió configuración. Un intento de PIN sin confirmar debe revisarse antes de repetirlo.

## Relación con los registros anteriores

Las [pruebas del 2026-10-19](2026-10-19-motores-esc.md) conservaron PWM aceptado sin giro observado y un intento de enlace fallido posterior. Los registros de [orientación](2026-10-19-orientacion-navigator.md) y [telemetría](2026-10-19-gps.md) conservan la calibración entonces pendiente, el armado transitorio y las caídas anteriores con causa sin determinar.

Esos hechos siguen fechados como históricos. La información nueva no demuestra por qué ocurrieron ni los sitúa automáticamente como fallos presentes. La evaluación de YOLO y la discrepancia de tasa GPS siguen como trabajo posterior.

La síntesis vigente y los siguientes ensayos están en [estado.md](../estado.md); los procedimientos están en [preparación](../preparacion.md).

## Verificación de la actualización documental

El comprobador del repositorio pasó con 54 archivos y 131 enlaces/anclas, sintaxis/configuración y patrones de secretos. También pasaron la comparación de las misiones regeneradas y el visor con telemetría simulada. Estas comprobaciones locales no ejecutan los ensayos pendientes del barco.
