# Acceso móvil a Kame con ZeroTier

Guía de la instalación documentada el **2026-10-16**: módem Luat Air780EG por USB en la Raspberry Pi 5 y red privada ZeroTier. Antes de usarla con el vehículo, revisar el [último estado observado](../../docs/estado.md) y comprobar el enlace en vivo.

## Componentes y rutas

| Componente | Configuración documentada |
| --- | --- |
| Módem Air780EG | `eth1` en `192.168.10.2/24`, gateway `192.168.10.1`, puerto AT `/dev/ttyACM1`. |
| Desbloqueo de SIM | `/usr/local/sbin/kame-air780eg-unlock.py`, `kame-air780eg-unlock.service` y `.timer`. PIN en `/etc/kame/air780eg-pin` (directorio `0700`, archivo `0600`). |
| ZeroTier en BlueOS | Extensión `williangalvani.zerotier` v1.14.3; identidad en `/usr/blueos/extensions/zerotier`. |
| ZeroTier en Windows | ZeroTier One 1.16.2, servicio `ZeroTierOneService` de inicio automático. |
| Red privada | ID e identidades de nodos en `local/red.md`, excluido de Git; PC `10.133.182.131` y Pi `10.133.182.55` en la sesión documentada. |

El archivo local `zerotier-local.conf` se instaló como `/usr/blueos/extensions/zerotier/local.conf` para excluir `192.168.2.0/24` y `eth0` del túnel y favorecer el módem. Los servicios y el script de desbloqueo tienen sus fuentes en esta carpeta. **No usar `/dev/ttyACM0` para comandos AT**: pertenece al GPS u-blox.

## Arranque automático y alcance

El temporizador de systemd se instaló en `/etc/systemd/system/kame-air780eg-unlock.timer`; llama a `kame-air780eg-unlock.service` 30 segundos después del arranque y vuelve a comprobar cada minuto. El servicio ejecuta el script de desbloqueo. Este busca el puerto AT del Air780EG, consulta `AT+CPIN?` y solo envía el PIN si la respuesta es `SIM PIN`; si el puerto no existe, termina sin hacer nada. Si un intento de PIN no se puede confirmar como `READY`, deja una marca y evita repetirlo a ciegas. El PIN sigue en el archivo protegido `/etc/kame/air780eg-pin`.

Este temporizador automatiza **la comprobación y el desbloqueo de la SIM**. Por sí mismo no demuestra que el módem esté presente, que `eth1` tenga conectividad, que la ruta de Internet salga por el módem o que ZeroTier esté operativo. Para validar 4G tras encender, comprobar que existe el puerto AT, que la SIM queda `READY`, que `eth1` tiene la ruta esperada y que ZeroTier está `ONLINE`; `listnetworks` con estado `OK` no sustituye esas comprobaciones. La extensión ZeroTier se administra en Extensions Manager de BlueOS, que normalmente inicia las extensiones instaladas al arrancar ([documentación de BlueOS](https://blueos.cloud/docs/stable/development/extensions/)); confirmar también que la extensión no esté deshabilitada.

La observación del 2026-10-19 encontró el temporizador habilitado y activo, pero módem USB, puerto AT y `eth1` ausentes, con `Air780EG AT port absent; nothing to do`. Es un antecedente de esa sesión, no una descripción de la presencia actual del módem. La situación vigente y los ensayos siguientes se consultan en [estado](../../docs/estado.md).

## Ensayo de arranque 4G

Preparar una tarea y registrar cada intento por separado, siguiendo [preparación](../../docs/preparacion.md). Realizar **dos encendidos consecutivos** del barco con el módem conectado desde antes de encender. El barco permanece desarmado y cada encendido/apagado físico debe estar supervisado y acordado.

Condiciones: módem/SIM instalados, cobertura disponible, PC con Internet independiente y ZeroTier preparado. La Pi no tiene otra salida a Internet: Ethernet no proporciona enlace y no hay un enlace Wi-Fi cliente con salida alternativa. El AP KAME puede permanecer activo. Preparar estas condiciones antes del ensayo; no cambiar la red o los servicios durante la medida para convertir un intento fallido en correcto.

Desde cada encendido, medir el tiempo hasta cumplir **todas** estas comprobaciones, con un máximo inicial de **cinco minutos por intento**:

1. Módem identificado y SIM lista. Revisar el estado mediante la información disponible y los registros del servicio; no introducir el PIN manualmente para aprobar el intento.
2. Interfaz móvil presente (documentada como `eth1`), configuración/ruta válida y salida efectiva por el módem. Verificar identidad y ruta, no solo el nombre de interfaz.
3. ZeroTier indica `ONLINE` y la red está disponible. `listnetworks: OK` por sí solo no basta.
4. Desde el PC independiente funcionan BlueOS y SSH por ZeroTier y se reciben heartbeat frescos con contador que avanza. Confirmar estado desarmado antes de continuar.

Las consultas de solo lectura desde el PC forman parte de la verificación. No debe ser necesario desbloquear la SIM, conectar la red, reiniciar procesos o arrancar servicios manualmente en el barco. Si se necesita cualquiera de esas intervenciones, ese intento no cumple, aunque después haya acceso.

El servicio de desbloqueo conserva el PIN en `/etc/kame/air780eg-pin`. Si hay un intento de PIN sin confirmar o existe `pin-attempt-pending`, registrarlo y revisar el estado antes de repetirlo; no borrar la marca ni forzar nuevos intentos para completar el ensayo. Verificar la identidad del puerto AT documentado antes de cualquier consulta manual y no abrir el puerto GPS que usa ArduPilot.

Registrar t0, tiempos de cada hito y de conexión completa, interfaz/ruta observadas, estados de ZeroTier, fuente de la lectura SIM, acceso BlueOS/SSH, heartbeat y estado final. Las dos repeticiones deben cumplir. Si falta acceso, recoger después los registros por un enlace de diagnóstico autorizado y mantener el resultado original como fallido o interrumpido, con el motivo; abrir una tarea concreta antes de modificar configuración.

Este ensayo valida la cadena completa. El temporizador SIM no demuestra por sí solo el resultado. El [vídeo por 4G](../video/README.md#ensayo-por-4g) se comprueba después como ensayo visual independiente.

## Conexión diaria por 4G

1. Dar Internet al PC y comprobar que ZeroTier One está ejecutándose. La Pi necesita el módem conectado, SIM lista y cobertura.
2. Abrir BlueOS en `http://10.133.182.55/`; abrir Cockpit desde el menú de BlueOS.
3. Para SSH desde el PC configurado, usar `ssh kame-4g`; desde otro equipo autorizado en la misma red, `ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password pi@10.133.182.55`. El alias del PC está en `C:\Users\Miguel\.ssh\config` y debe solicitar la contraseña de `pi` guardada en `local/credenciales.md`.
4. Si se necesita RTSP directo, usar `rtsp://10.133.182.55:8554/cam` para cámara original o `rtsp://10.133.182.55:8556/yolo` para la imagen anotada. BlueOS/Cockpit anunciaban solo YOLO después del ajuste del 2026-10-16.

La red ZeroTier es privada y ambos extremos necesitan Internet. La ruta predeterminada de la Pi debe seguir por el módem `eth1`; no usar ZeroTier como salida general. Al entrar en Cockpit por otra IP, seleccionar el mismo usuario y, si aparece conflicto de ajustes, elegir **Use the value from BlueOS** y recargar. La selección de perfil/vista puede ser local a cada navegador.

Las credenciales están en el archivo privado `local/credenciales.md` de la raíz, excluido de Git. Leer las [reglas de acceso](../../AGENTS.md#credenciales-y-archivos-locales) y comprobar si siguen vigentes antes de usarlas. En la instalación actual SSH usa **contraseña**, no una clave privada del PC. OpenSSH prueba automáticamente claves de `~/.ssh/` si no se le indica lo contrario; que una de ellas sea rechazada no significa que la contraseña del proyecto haya fallado. Para el alias `kame-4g`, configurar `PubkeyAuthentication no` y `PreferredAuthentications password`. No usar `BatchMode=yes` al conectar manualmente, porque desactiva la petición de contraseña.

## Conexión por Ethernet (SSH)

La interfaz Ethernet de la Raspberry (`eth0`) está documentada con `192.168.2.2/24`; BlueOS se abre en `http://192.168.2.2/`. Para SSH desde Windows, conectar el PC a esa red y ejecutar:

```powershell
Test-NetConnection 192.168.2.2 -Port 22
ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password pi@192.168.2.2
```

En una conexión directa por cable, si Windows no obtiene una dirección de la red, asignar al adaptador Ethernet del PC una dirección libre de `192.168.2.0/24` (máscara `255.255.255.0`). No asignar `192.168.2.2` al PC. Para el enlace directo no hace falta configurar puerta de enlace ni DNS. Si el PC ya tiene una dirección en esa subred por la red a la que está conectado, no hace falta cambiarla.

El usuario SSH documentado es `pi`; la contraseña privada está en `local/credenciales.md`. Consultarla solo según las [reglas de acceso](../../AGENTS.md#credenciales-y-archivos-locales), y no escribirla en el comando ni compartirla. `ssh kame-4g` es el alias para ZeroTier/4G y no apunta a Ethernet.

## Comprobaciones de solo lectura

Para la salida previa al agua del 2026-10-21, el [ensayo estático conjunto de cinco minutos](../../docs/preparacion.md#ensayo-estático-conjunto-de-cinco-minutos-antes-de-botar) registra 4G, GPS, heartbeat y vídeo observado en Cockpit. El capturador `ensayo_5min.py` admite `simular`, `preflight`, `capture --confirmar-condiciones`, `marca` y `resumen`. Solo `preflight` y `capture` acceden al barco; los datos crudos quedan en `local/registros/F1-4G-SENSORES-20261021-01/`. La comprobación automática no sustituye la observación continua de la pestaña ni el juicio sobre la posición GPS.

En la Raspberry:

```sh
ip route get 1.1.1.1
systemctl status --no-pager kame-air780eg-unlock.timer
journalctl -u kame-air780eg-unlock.service -n 20 --no-pager
docker exec extension-williangalvanizerotierv1143 zerotier-cli info
docker exec extension-williangalvanizerotierv1143 zerotier-cli listnetworks
docker exec extension-williangalvanizerotierv1143 zerotier-cli peers
```

En Windows PowerShell, mantener privado el token local:

```powershell
$ztToken = (Get-Content -Raw "$env:LOCALAPPDATA\ZeroTier\authtoken.secret").Trim()
& 'C:\Program Files (x86)\ZeroTier\One\zerotier-cli.bat' "-T$ztToken" listnetworks
& 'C:\Program Files (x86)\ZeroTier\One\zerotier-cli.bat' "-T$ztToken" peers
```

Si la SIM indica `SIM PIN` tras reconectar el módem, el temporizador consulta el estado y envía el PIN solo si hace falta. Si un intento no confirma `READY`, crea `/var/lib/kame-air780eg/pin-attempt-pending` y no repite el PIN; comprobarlo manualmente antes de borrar esa marca. No hay una prueba documentada de un ciclo físico completo de desconexión y recuperación.

El 2026-10-16, con Ethernet desconectado, BlueOS y SSH respondieron por ZeroTier y el PC decodificó el RTSP YOLO. El par ZeroTier figuraba en `RELAY`; dos vídeos simultáneos consumieron cerca del caudal de subida 4G observado y elevaron la latencia. Las medidas exactas y sus límites están en el [registro del 16 de octubre](../../docs/historial/2026-10-16-integracion.md). Antes de operar, comprobar telemetría e imagen WebRTC **dentro de Cockpit** en el enlace real.

## Reversión

Antes de cambiar la red o los servicios, revisar las [reglas de actuación](../../AGENTS.md). Para retirar el acceso remoto, desinstalar la extensión ZeroTier desde **Extensions Manager** de BlueOS y salir de la red privada en Windows o desinstalar ZeroTier One. Para desactivar solo el desbloqueo automático de SIM:

```sh
sudo systemctl disable --now kame-air780eg-unlock.timer
```

Ese comando no elimina el archivo del PIN ni cambia el GPS o el autopiloto. Desautorizar un nodo en [ZeroTier Central](https://central.zerotier.com/) corta su acceso a la red privada.
