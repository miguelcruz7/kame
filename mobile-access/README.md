# Acceso móvil a Kame con ZeroTier

Guía de la instalación documentada el **2026-10-16**: módem Luat Air780EG por USB en la Raspberry Pi 5 y red privada ZeroTier. Antes de usarla con el vehículo, revisar el [último estado observado](../docs/estado.md) y comprobar el enlace en vivo.

## Componentes y rutas

| Componente | Configuración documentada |
| --- | --- |
| Módem Air780EG | `eth1` en `192.168.10.2/24`, gateway `192.168.10.1`, puerto AT `/dev/ttyACM1`. |
| Desbloqueo de SIM | `/usr/local/sbin/kame-air780eg-unlock.py`, `kame-air780eg-unlock.service` y `.timer`. PIN en `/etc/kame/air780eg-pin` (directorio `0700`, archivo `0600`). |
| ZeroTier en BlueOS | Extensión `williangalvani.zerotier` v1.14.3; identidad en `/usr/blueos/extensions/zerotier`. |
| ZeroTier en Windows | ZeroTier One 1.16.2, servicio `ZeroTierOneService` de inicio automático. |
| Red privada | ID `ID_ZEROTIER_PRIVADO`; PC `10.133.182.131` y Pi `10.133.182.55` en la sesión documentada. |

El archivo local `zerotier-local.conf` se instaló como `/usr/blueos/extensions/zerotier/local.conf` para excluir `192.168.2.0/24` y `eth0` del túnel y favorecer el módem. Los servicios y el script de desbloqueo tienen sus fuentes en esta carpeta. **No usar `/dev/ttyACM0` para comandos AT**: pertenece al GPS u-blox.

## Arranque automático y alcance

El temporizador de systemd se instaló en `/etc/systemd/system/kame-air780eg-unlock.timer`; llama a `kame-air780eg-unlock.service` 30 segundos después del arranque y vuelve a comprobar cada minuto. El servicio ejecuta el script de desbloqueo. Este busca el puerto AT del Air780EG, consulta `AT+CPIN?` y solo envía el PIN si la respuesta es `SIM PIN`; si el puerto no existe, termina sin hacer nada. Si un intento de PIN no se puede confirmar como `READY`, deja una marca y evita repetirlo a ciegas. El PIN sigue en el archivo protegido `/etc/kame/air780eg-pin`.

Este temporizador automatiza **la comprobación y el desbloqueo de la SIM**. Por sí mismo no demuestra que el módem esté presente, que `eth1` tenga conectividad, que la ruta de Internet salga por el módem o que ZeroTier esté operativo. Para validar 4G tras encender, comprobar que existe el puerto AT, que la SIM queda `READY`, que `eth1` tiene la ruta esperada y que ZeroTier está `ONLINE`; `listnetworks` con estado `OK` no sustituye esas comprobaciones. La extensión ZeroTier se administra en Extensions Manager de BlueOS, que normalmente inicia las extensiones instaladas al arrancar ([documentación de BlueOS](https://blueos.cloud/docs/stable/development/extensions/)); confirmar también que la extensión no esté deshabilitada.

La observación en vivo del 2026-10-19 encontró el temporizador habilitado y activo, pero el módem USB, el puerto AT y `eth1` ausentes. El registro del servicio decía `Air780EG AT port absent; nothing to do`. Por eso aún falta una prueba de arranque en frío con el módem conectado; ver el [estado observado](../docs/estado.md).

## Conexión diaria

1. Dar Internet al PC y comprobar que ZeroTier One está ejecutándose. La Pi necesita el módem conectado, SIM lista y cobertura.
2. Abrir BlueOS en `http://10.133.182.55/`; abrir Cockpit desde el menú de BlueOS.
3. Para SSH desde el PC configurado, usar `ssh kame-4g`; desde otro equipo autorizado en la misma red, `ssh pi@10.133.182.55`. El alias del PC está en `C:\Users\Miguel\.ssh\config`.
4. Si se necesita RTSP directo, usar `rtsp://10.133.182.55:8554/cam` para cámara original o `rtsp://10.133.182.55:8556/yolo` para la imagen anotada. BlueOS/Cockpit anunciaban solo YOLO después del ajuste del 2026-10-16.

La red ZeroTier es privada y ambos extremos necesitan Internet. La ruta predeterminada de la Pi debe seguir por el módem `eth1`; no usar ZeroTier como salida general. Al entrar en Cockpit por otra IP, seleccionar el mismo usuario y, si aparece conflicto de ajustes, elegir **Use the value from BlueOS** y recargar. La selección de perfil/vista puede ser local a cada navegador.

El usuario, la contraseña SSH y el PIN de la SIM están en [AGENTS.md](../AGENTS.md#credenciales-documentadas). La contraseña documentada seguía siendo la predeterminada el 2026-10-16; comprobar si ha cambiado antes de usarla.

## Comprobaciones de solo lectura

En la Raspberry:

```sh
ip route get 1.1.1.1
systemctl status --no-pager kame-air780eg-unlock.timer
journalctl -u kame-air780eg-unlock.service -n 20 --no-pager
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

El 2026-10-16, con Ethernet desconectado, BlueOS y SSH respondieron por ZeroTier y el PC decodificó el RTSP YOLO. El par ZeroTier figuraba en `RELAY`; dos vídeos simultáneos consumieron cerca del caudal de subida 4G observado y elevaron la latencia. Las medidas exactas y sus límites están en el [registro del 16 de octubre](../docs/historial/2026-10-16-integracion.md). Antes de operar, comprobar telemetría e imagen WebRTC **dentro de Cockpit** en el enlace real.

## Reversión

Antes de cambiar la red o los servicios, revisar las [reglas de actuación](../AGENTS.md). Para retirar el acceso remoto, desinstalar la extensión ZeroTier desde **Extensions Manager** de BlueOS y salir de la red privada en Windows o desinstalar ZeroTier One. Para desactivar solo el desbloqueo automático de SIM:

```sh
sudo systemctl disable --now kame-air780eg-unlock.timer
```

Ese comando no elimina el archivo del PIN ni cambia el GPS o el autopiloto. Desautorizar un nodo en [ZeroTier Central](https://central.zerotier.com/) corta su acceso a la red privada.
