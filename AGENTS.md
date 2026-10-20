# Instrucciones para trabajar en Kame

## Objetivo y documentación

Avanzar primero en [SITL](sitl/README.md), luego probar el vehículo en condiciones controladas y finalmente considerar pruebas en el mar. Leer [el estado observado](docs/estado.md) y la guía del subsistema correspondiente antes de actuar. Las observaciones fechadas son históricas hasta que se vuelvan a verificar.

## Inspección inicial del vehículo

1. Elegir el enlace disponible: Wi-Fi `KAME` (`http://192.168.42.1/`), Ethernet (`http://192.168.2.2/`) o ZeroTier/4G (`http://10.133.182.55/`).
2. Empezar con consultas de solo lectura. Confirmar heartbeat MAVLink y estado de armado; leer `GPS_RAW_INT` (fix, satélites y coordenadas), avisos de prearm/brújula y estado de cámara y vídeo.
3. Registrar fecha, enlace usado, fuente de cada lectura y cualquier dato que no haya podido comprobarse. No inferir el estado de un componente a partir de otro: HTTP 200 de BlueOS no demuestra telemetría ni reproducción WebRTC.

## Vía de interacción con BlueOS y el vehículo

- Priorizar consultas de solo lectura por API documentada de BlueOS, MAVLink/MAVLink2REST o SSH para comprobar sensores, parámetros, asignaciones, servicios y registros. Verificar que el endpoint y su respuesta corresponden a la versión instalada; no asumir que una lectura histórica sigue vigente.
- Usar la interfaz web cuando aporte una comprobación visual o una función sin API fiable. En particular, confirmar en Cockpit que el vídeo WebRTC muestra una imagen actual y fluida: un RTSP operativo o una fuente anunciada por BlueOS no lo demuestran.
- Para un cambio expresamente autorizado, guardar antes el valor o configuración vigente, aplicar solo el cambio acordado mediante una vía documentada y leer después el estado resultante. Registrar el valor anterior, el nuevo, la fecha y el resultado. Respetar siempre los límites de actuación siguientes.

## Credenciales documentadas

Las credenciales operativas están en `local/credenciales.md`, excluido de Git. El PIN instalado permanece en `/etc/kame/air780eg-pin`. No copiar contraseñas, PIN, tokens ni identidades privadas a archivos versionados.

## Límite de actuación

No cambiar parámetros, firmware o asignaciones de puerto, ni reiniciar, armar o accionar motores sin autorización explícita y comprobación de seguridad. Mantener el vehículo desarmado mientras existan avisos de brújula o no se haya validado el GPS. Los procedimientos de diagnóstico y reversión de [vídeo](yolo-cockpit/README.md) y [red móvil](mobile-access/README.md) deben leerse antes de usarse.

## Registro

Actualizar [docs/estado.md](docs/estado.md) con la última observación verificable y mover mediciones e incidencias extensas a [docs/historial/](docs/historial/README.md). Mantener las credenciales operativas en el archivo local privado cuando cambien; no publicar tokens locales. El inventario y los puertos están en [docs/hardware.md](docs/hardware.md).
