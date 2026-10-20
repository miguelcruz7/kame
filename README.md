# Kame

Proyecto del vehículo Kame: autopiloto Navigator64 con ArduRover, cámara IMX462, vídeo YOLO en BlueOS/Cockpit y acceso remoto por módem móvil. La secuencia de trabajo prevista es SITL, pruebas controladas con el vehículo y, después de resolver las comprobaciones pendientes, pruebas en el mar.

## Dónde encontrar cada cosa

| Documento | Contenido principal |
| --- | --- |
| [Contexto general](context.md) | Resumen de incorporación del proyecto para agentes nuevos. |
| [AGENTS.md](AGENTS.md) | Reglas para el agente: inspección inicial y límites de actuación. |
| [Estado observado](docs/estado.md) | Última lectura documentada y comprobaciones pendientes. |
| [Hardware e interfaces](docs/hardware.md) | Inventario, conexiones, direcciones y [montaje/calibración pendiente del Navigator](docs/hardware.md#navigator-montaje-y-calibración-pendiente). |
| [SITL](sitl/README.md) | Arranque local del simulador y misiones de ejemplo. |
| [Vídeo YOLO](yolo-cockpit/README.md) | Arquitectura, operación de los streams y reversión. |
| [Acceso móvil](mobile-access/README.md) | Uso de ZeroTier/4G, diagnóstico y reversión. |
| [Visor de telemetría](navigator-imu-viewer/README.md) | Arranque del visor 3D de solo lectura. |
| [Historial](docs/historial/README.md) | Pruebas e incidencias fechadas. |

## Acceso a BlueOS

| Enlace del PC | Dirección de BlueOS |
| --- | --- |
| Wi-Fi `KAME` | `http://192.168.42.1/` |
| Ethernet | `http://192.168.2.2/` |
| ZeroTier mediante 4G | `http://10.133.182.55/` |

Las direcciones son las documentadas en la instalación. Antes de operar, comprobar en vivo la conectividad, el heartbeat, `GPS_RAW_INT`, los avisos de brújula y el vídeo. La última observación está en [estado.md](docs/estado.md) y el ajuste de orientación previo a la recalibración en el [historial del Navigator](docs/historial/2026-10-19-orientacion-navigator.md).

Las credenciales operativas documentadas están en [AGENTS.md](AGENTS.md#credenciales-documentadas). El PIN de la SIM instalada también se conserva en la Raspberry en `/etc/kame/air780eg-pin`, con permisos restringidos.
