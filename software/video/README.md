# Vídeo YOLO26n en BlueOS y Cockpit

La instalación documentada genera H.264 anotado con YOLO26n NCNN FP16 en una Raspberry Pi 5. Detecta únicamente las clases COCO `person` (0) y `boat` (8), con entrada 320×320 y umbral `conf=0.15`. Esta guía describe la configuración dejada el **2026-10-16**; comprobar su [estado en vivo](../../docs/estado.md) antes de intervenir.

## Arquitectura y configuración documentada

```text
Cámara IMX462 → kame-mediamtx.service → RTSP /cam (8554, 1920×1080)
                                           ↓
                         kame-yolo-detect.service (NCNN, ~8 inferencias/s)
                                           ↓
                     kame-yolo-mediamtx.service → RTSP /yolo (8556, 960×540/8 FPS)
                                           ↓
                         BlueOS Redirect / MAVLink Camera Manager → WebRTC → Cockpit
```

- Ambas instancias MediaMTX escuchan en `0.0.0.0`; el detector lee `/cam` y publica `/yolo` por `127.0.0.1` dentro de la Pi. Los clientes RTSP deben usar la IP de su enlace, indicada en [hardware e interfaces](../../docs/hardware.md#red-y-puertos).
- `/cam` conserva el servicio original `kame-mediamtx.service`. BlueOS Video Streams anuncia **solo** `YOLO26n Person + Boat` como fuente Redirect, H.264 960×540/8 FPS, con MAVLink habilitado. El endpoint configurado en el Redirect es `rtsp://192.168.2.2:8556/yolo`, que Mavlink Camera Manager abre dentro de la propia Pi. `/cam` sigue disponible directamente por RTSP.
- `kame-yolo-detect.service` solicita 8 inferencias/s y publica a 8 FPS nominales. La cuota documentada es `CPUQuota=150%` y `Nice=15`. Si la lectura acumula más de 1,5 s de retraso, reconecta la entrada para descartar la cola. El watchdog recupera bloqueos y aparece `VIDEO SIN DATOS - RECONECTANDO` si la imagen queda obsoleta.
- Las cajas persisten un máximo de dos inferencias perdidas, en gris y con etiqueta `hold`. Esto es solo ayuda visual; no constituye seguimiento fiable.

## Archivos locales y en la Pi

| Proyecto | Destino documentado |
| --- | --- |
| `yolo_stream.py` | `/opt/kame-yolo/yolo_stream.py` |
| `deploy/mediamtx-camera.yml` | `/opt/kame-camera/mediamtx.yml` |
| `deploy/mediamtx.yml` | `/opt/kame-yolo/mediamtx.yml` |
| `deploy/kame-yolo-mediamtx.service`, `deploy/kame-yolo-detect.service` | `/etc/systemd/system/` |
| Modelo local `local/modelos/model-fp16-320/yolo26n_ncnn_model/` (desde la raíz) | `/home/pi/kame-yolo-offline/model-fp16-320/yolo26n_ncnn_model/` |

El entorno Python documentado está en `/home/pi/kame-yolo-offline/venv`; el binario MediaMTX compartido, en `/opt/kame-camera/mediamtx`. `deploy/configure_cockpit_yolo_only.py` contiene la modificación de perfiles aplicada el 2026-10-16. Los respaldos y resultados de aquella intervención están en el [registro del 16 de octubre](../../docs/historial/2026-10-16-integracion.md).

## Abrir el vídeo en Cockpit

1. Abrir BlueOS por el enlace disponible de la [tabla de acceso](../../docs/hardware.md#red-y-puertos) y entrar en Cockpit.
2. Elegir el usuario **JLOUREDA**. Los perfiles **ROV default**, **Boat default** y **MAV default** quedaron con un `VideoPlayer` por vista, asociado a `Stream 1 → YOLO26n Person + Boat`. En **Boat default / Map view** se conservó el reproductor grande.
3. Al cambiar de dirección IP o navegador, volver a elegir usuario, perfil y vista. Si Cockpit avisa de conflicto de ajustes, seleccionar **Use the value from BlueOS** y recargar. Los navegadores que estaban abiertos durante el cambio también necesitan recarga.
4. Confirmar que la imagen corresponde a la escena **actual** y se reproduce dentro del navegador. RTSP y señalización WebRTC se comprobaron por 4G, pero esa prueba visual final seguía pendiente el 2026-10-16.

El acceso directo al RTSP YOLO por cada enlace figura en [hardware e interfaces](../../docs/hardware.md#red-y-puertos). Un GCS que use literalmente la URL anunciada por MAVLink puede requerir sustituir `192.168.2.2` por la IP de su enlace.

## Inspección y control del servicio

Lecturas en la Pi:

```sh
systemctl status --no-pager kame-mediamtx.service kame-yolo-mediamtx.service kame-yolo-detect.service
journalctl -u kame-yolo-mediamtx.service -u kame-yolo-detect.service -n 50 --no-pager
vcgencmd measure_temp
vcgencmd get_throttled
```

Antes de cambiar servicios, revisar su estado y las [reglas de actuación](../../AGENTS.md). Para arrancar solo YOLO:

```sh
sudo systemctl start kame-yolo-mediamtx.service kame-yolo-detect.service
```

Para detener temporalmente solo YOLO:

```sh
sudo systemctl stop kame-yolo-detect.service kame-yolo-mediamtx.service
```

Conservar `kame-mediamtx.service`: sirve `/cam` y aporta la entrada original al detector.

## Límites de uso

El modelo COCO no está entrenado ni validado para escenas marítimas de esta cámara. La entrada 320×320 puede perder personas o barcos pequeños/lejanos; `conf=0.15` necesita evaluación de falsas alarmas. La prueba de integración verificó decodificación, carga y disponibilidad de streams, pero no una detección positiva conocida, precisión ni recall. Tratar esta salida como prototipo, sin usarla como sistema de seguridad o navegación autónoma. El plan de validación está en [estado observado](../../docs/estado.md).

## Reversión de YOLO

El respaldo de perfiles y fuentes previo a la vista con un solo vídeo está en `/home/pi/cockpit-video-before-yolo-only-20261016-171853.json`; el de claves ICE, en `/home/pi/cockpit-ice-before-4g-20261016-172621.json`. Para recuperar dos fuentes anunciadas, restaurar los perfiles/correspondencias desde el respaldo y recrear el Redirect original `Waveshare IMX462 1080p20` con `rtsp://192.168.2.2:8554/cam`. Si se elimina YOLO por completo, retirar su Redirect después de restaurar la cámara original.

Para deshabilitar solo las dos unidades YOLO:

```sh
sudo systemctl disable --now kame-yolo-detect.service kame-yolo-mediamtx.service
```

Si también se desinstala, borrar únicamente esas dos unidades y `/opt/kame-yolo/`, luego ejecutar `sudo systemctl daemon-reload`. Retirar `/home/pi/kame-yolo-offline/` solo si ya no se necesita el entorno/modelo. **No borrar** `/opt/kame-camera/mediamtx` ni detener `kame-mediamtx.service`: pertenecen a `/cam`.

Las mediciones de la versión inicial a 5 FPS están en [2026-10-09](../../docs/historial/2026-10-09-video.md), las incidencias de Cockpit en [2026-10-13](../../docs/historial/2026-10-13-conectividad.md) y los cambios a 8 FPS y una sola fuente en [2026-10-16](../../docs/historial/2026-10-16-integracion.md).

## Recursos y desarrollo local

Los modelos y wheels originales están en `local/modelos/` y `local/wheels/`, desde la raíz del proyecto. Sus hashes figuran en el [inventario de recursos](../../docs/historial/recursos.json). Las versiones de los wheels no constituyen un lockfile de un entorno verificado. Recuperar los archivos por hash desde el respaldo privado cuando se trabaje desde otro clon; la procedencia de descarga de varios archivos sigue pendiente. La metadata local del modelo FP16/320 declara Ultralytics 8.4.174 y AGPL-3.0; revisar licencias antes de distribuir.

Las capturas de referencia y el registro crudo de Cockpit se conservan en `local/registros/video/`; el historial enlaza su índice. La reestructuración no modifica código del detector, umbrales, servicios ni rutas instaladas en la Pi.
