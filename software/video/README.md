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

## Diagnóstico de IP de vídeo bloqueadas

El aviso **All available video stream IPs are being blocked** indica que la sesión ha encontrado direcciones ICE, pero ninguna coincide con su selección permitida. No equivale a una pérdida de conexión del vehículo. El [diagnóstico separado del 2026-10-20](../../docs/historial/2026-10-20-video-cockpit-4g.md) conserva las fuentes y los límites actuales.

En el [código de Cockpit v1.16.0-beta.1](https://github.com/bluerobotics/cockpit/blob/v1.16.0-beta.1/src/libs/webrtc/session.ts), una lista permitida vacía no filtra por IP. La [rutina del aviso](https://github.com/bluerobotics/cockpit/blob/v1.16.0-beta.1/src/stores/video.ts) se instala si la selección automática está habilitada al inicializar el módulo. La [sincronización de ajustes](https://github.com/bluerobotics/cockpit/blob/v1.16.0-beta.1/src/composables/settingsSyncer.ts) utiliza primero el almacenamiento del navegador y después consulta BlueOS. Por tanto, leer `[]` y selección automática desactivada en BlueOS no demuestra qué valores aplicó una pestaña ya abierta. Comprobar también versión, usuario y conflictos de sincronización antes de atribuir una causa definitiva.

**Resultado del 2026-10-20:** la sesión Edge del usuario tenía seleccionada `192.168.10.2` y selección automática activada, pese a los valores distintos guardados en BlueOS. Se seleccionó `10.133.182.55`, se desactivó la selección automática y se recargó una vez: YOLO apareció a 960×540 y el usuario confirmó reproducción. No se cambió el encoder ni ningún servicio. El usuario solicitó detener la observación y omitir el ensayo de 15 min; los ensayos ampliados siguientes son procedimientos pendientes, no resultados acreditados.

### Aislamiento de un estudio de desconexiones

Trabajar en un worktree y rama propios aísla archivos, pero no los servicios ni los ajustes compartidos del barco. Mientras otro estudio esté activo, limitarse a documentación, código y lecturas de configuración acordadas. No abrir otro reproductor, decodificar RTSP, medir caudal, cambiar usuario/perfiles/ajustes, reiniciar servicios ni alterar red o telemetría. No abrir una pestaña adicional de Cockpit como lectura pasiva: puede iniciar vídeo y sincronizar ajustes automáticamente.

Mantener ID y registros separados para vídeo y conectividad. Los datos de otro estudio pueden consultarse como antecedentes, conservando su origen y hora, sin copiar ni modificar sus archivos. Las pruebas activas requieren una ventana independiente confirmada por el usuario; no se infiere una pausa por el tiempo transcurrido.

### Corrección selectiva en una ventana de vídeo

1. Confirmar fin o pausa del estudio paralelo, barco desarmado y un único consumidor remoto. Identificar versión de Cockpit, navegador, URL, usuario, perfil y vista. La dirección de entrada para 4G es `http://10.133.182.55/extensionv2/cockpit/#/`.
2. Guardar el estado anterior bajo el ID del ensayo en `local/registros/`: captura de Settings → Video y valores del usuario afectado en BlueOS, incluidos IP permitidas, selección automática, protocolos permitidos y correspondencia de streams. Conservar respaldo completo del usuario de forma privada antes de modificar; los informes públicos solo incluyen los valores de vídeo pertinentes. Comparar los valores efectivos del navegador con BlueOS. No volcar todo el almacenamiento del navegador a un informe.
3. En **Main menu → Settings → Video**, quitar las IP incompatibles y seleccionar `10.133.182.55` si aparece entre las disponibles. Registrar valores anterior/nuevo. Si no aparece, conservar la evidencia e inspeccionar el anuncio de candidatos; no seleccionar una dirección Ethernet inaccesible ni cambiar el Redirect a ciegas.
4. Confirmar `Stream 1 → YOLO26n Person + Boat`. Si surge un conflicto de sincronización, comparar el respaldo y elegir el valor de vídeo acordado; no aceptar globalmente ajustes de otros componentes. Recargar una vez y comprobar persistencia. No ejecutar `deploy/configure_cockpit_yolo_only.py`: reescribe perfiles de varios usuarios y puede eliminar otra fuente anunciada.
5. Verificar por separado desaparición del aviso, conexión ICE/DTLS y frames decodificados de la escena actual. Registrar candidata seleccionada, bytes/frames recibidos y decodificados, pérdidas, pausas y retraso. Si falta imagen, obtener señalización y métricas antes de proponer cambios.

Una respuesta RTSP a DESCRIBE anuncia formato, pero no acredita frames actuales. Una conexión WebSocket aceptada tampoco demuestra negociación completa ni transporte multimedia. Si el aviso desaparece sin imagen: sin pareja ICE, revisar rutas/candidatos; con pareja y sin bytes, revisar pipeline/transporte; con bytes y sin frames decodificados, revisar SDP/H.264/paquetes. Comparar `/cam` y `/yolo` dentro de la Pi durante la ventana acordada para evitar enviar dos vídeos por 4G.

### Validación ampliada y reversión

Mantener inicialmente 960×540/8 FPS. Tras superar el ensayo visual de 60 s, observar **15 min por 4G**, sin errores ni congelaciones superiores a un segundo y sin retraso creciente; medir y registrar el retraso con movimientos conocidos o una referencia temporal visible. Reabrir Cockpit tres veces: primera imagen en un máximo de 15 s y sin repetición del bloqueo. Comprobar después 60 s por Wi-Fi con su dirección accesible, y volver a confirmar la selección para 4G si se modificó.

Solo si hay imagen y las métricas demuestran congestión, preparar un cambio separado a 640×360/8 FPS, objetivo 600 kb/s, máximo 750 kb/s y fotogramas clave cada segundo. El encoder actual fija 1.200.000 bit/s en código: este perfil requiere implementación, respaldo y verificación propios; no existe aún un ajuste de entorno que lo active. No reducir calidad para ocultar un bloqueo de candidatos.

Para revertir, restaurar exclusivamente los valores de vídeo modificados del usuario afectado desde el respaldo inmediato; recargar y leer de nuevo. No restaurar un perfil completo sobre cambios concurrentes ni usar respaldos históricos como si fueran el estado anterior de esta sesión. Registrar corrección, instalación y validación por separado. El estudio del estado conectado/desconectado mantiene su propia causa y criterios.

## Ensayo por Wi-Fi KAME

Preparar una tarea de ensayo y seguir [preparación](../../docs/preparacion.md). Con el barco desarmado y supervisado, conectar el PC a KAME y abrir BlueOS/Cockpit por `192.168.42.1`. Registrar navegador, perfil, vista, fuente y enlace utilizados.

Observar el reproductor de Cockpit durante **60 segundos** e introducir movimientos conocidos en la escena al inicio, durante la observación y al final. No hace falta mover el barco ni accionar motores. Confirmar que la imagen sigue esos cambios y mantiene reproducción continua, sin congelaciones ni errores del reproductor. Anotar pausas y retraso observado; si no se midió un retraso, indicarlo en vez de inventar una cifra.

Registrar hora y resultado, evidencias de la escena actual y estado final. Una captura aislada, RTSP decodificable, procesos activos o señalización WebRTC no sustituyen la observación completa en Cockpit. Si falla, abrir una tarea de diagnóstico con los síntomas y registros antes de proponer cambios; no cerrar el ensayo como correcto después de una recuperación manual sin registrar la incidencia.

## Ensayo por 4G

Validar antes la [conexión automática y la ruta móvil](../conectividad/README.md#ensayo-de-arranque-4g). La Pi no debe depender de otra salida a Internet y el PC utiliza Internet independiente, accediendo a Cockpit por ZeroTier (`10.133.182.55`). El PC no usa KAME ni Ethernet hacia el barco durante este ensayo.

Repetir los **60 segundos**, movimientos conocidos, registro de pausas/retraso y criterio visual del [ensayo Wi-Fi](#ensayo-por-wi-fi-kame). Registrar como tarea y resultado independientes. Confirmar la ruta móvil realmente utilizada; poder abrir la dirección ZeroTier sin conocer esa ruta no demuestra que el vídeo haya pasado por 4G.

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
