# Historial de Kame

Las entradas registran lo observado o cambiado en su fecha. La síntesis más reciente del vehículo está en [estado.md](../estado.md); las operaciones están en [preparación](../preparacion.md) y en las guías de [vídeo](../../software/video/README.md) y [conectividad](../../software/conectividad/README.md).

| Fecha | Registro |
| --- | --- |
| 2026-10-09 | [Cámara CSI e integración inicial de YOLO](2026-10-09-video.md). |
| 2026-10-13 | [Conectividad, Cockpit y GPS](2026-10-13-conectividad.md). |
| 2026-10-16 | [GPS, vídeo, brújulas y acceso móvil](2026-10-16-integracion.md). |
| 2026-10-19 | [GPS y pérdida de telemetría](2026-10-19-gps.md). |
| 2026-10-19 | [Orientación del Navigator](2026-10-19-orientacion-navigator.md). |
| 2026-10-19 | [Diagnóstico de motores y ESC](2026-10-19-motores-esc.md). |
| 2026-10-20 | [Reestructuración y verificaciones locales](2026-10-20-reestructuracion.md). |
| 2026-10-20 | [Comunicación del usuario: MMC5983 desconectada y AK09915 como única brújula](2026-10-20-brujula-mmc5983.md). |
| 2026-10-20 | [Estado operativo comunicado y ensayos pendientes](2026-10-20-estado-operativo.md). |
| 2026-10-20 | [Detección USB y ruta del módem Air780EG](2026-10-20-deteccion-air780eg.md). |
| 2026-10-20 | [Muestra de calidad de la conexión 4G](2026-10-20-calidad-4g.md). |
| 2026-10-20 | [Ensayo estático 4G: errores RX, RELAY y telemetría antigua en Cockpit](2026-10-20-4g-estatico.md). |
| 2026-10-20 | [Cockpit: pausas de telemetría por 4G y diagnóstico abierto](2026-10-20-cockpit-4g.md). |
| 2026-10-20 | [Vídeo Cockpit por 4G: filtro de IP y ventana de validación pendiente](2026-10-20-video-cockpit-4g.md). |
| 2026-10-20 | [PWM3: fallo de arranque de WebAssistant y recuperación de ArduPilot](2026-10-20-pwm3-webassistant.md). |
| 2026-10-20 | [PWM3: ArduPilot usa un bus I²C distinto del chip PWM en Pi 5](2026-10-20-pwm3-controlador.md). |
| 2026-10-20 | [Adecuación del firmware oficial de Kame al barco y Raspberry Pi 5](2026-10-20-firmware-pi5.md). |
| 2026-10-20 | [PWM3: ensayo de neutro de 10 segundos por el bus físico 3](2026-10-20-pwm3-neutro-bus3.md). |
| 2026-10-20 | [Repetición de la verificación I²C PWM: bloqueada por ensayo de neutro concurrente](2026-10-20-pwm-i2c-verificacion.md). |
| 2026-10-20 | [BlueOS: adaptación I²C del PWM omitida por el bus real de la cámara](2026-10-20-blueos-i2c-camara.md). |
| 2026-10-20 | [Firmware PWM de Pi 5: compilación, instalación, verificación tras encendido y comunicación posterior de motores](2026-10-20-pwm-pi5-reparacion.md). |
| 2026-10-20 | [Publicación en GitHub y revisión del contenido público](2026-10-20-publicacion-github.md). |

## Archivos de evidencia

Los [snapshots de parámetros](parametros/README.md) se conservan como texto revisado. Los archivos pesados o crudos están en `local/`, excluido de Git, y el [inventario de recursos](recursos.json) recoge ruta local, tamaño, SHA-256 y procedencia conocida. Los hashes identifican archivos; su recuperación depende de conservar el respaldo privado.

El registro de 30 muestras de Cockpit del 13 de octubre está en `local/registros/video/cockpit-live-observation-2026-10-13.txt`. Las capturas están en `local/registros/video/screenshots/`, las dos fotos originales en `local/registros/camara/` y el DataFlash original en `local/registros/autopiloto/00000054.BIN`. Ese archivo no se atribuye a una sesión más reciente sin identificarla.

## Registrar un ensayo nuevo

Crear una entrada fechada con un ID común para sus archivos: objetivo y criterio de fase, fecha/zona horaria, entorno/enlace, versión Git y cambios locales, configuración antes/después, condiciones y autorización, resultado esperado/observado, métricas, evidencias recuperables con hash y estado final/reversión. Una intervención local de software se distingue de una observación del vehículo.
