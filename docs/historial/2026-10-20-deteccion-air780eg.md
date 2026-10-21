# Detección del módem Air780EG — 2026-10-20

**ID:** `F1-4G-DETECCION-20261020-01`  
**Objetivo:** comprobar de forma simple si BlueOS detectaba el módem USB conectado por el usuario.  
**Fecha y zona:** 2026-10-20 19:30 CEST.  
**Fuente y autorización:** lectura directa del asistente por SSH, autorizada por el usuario para comprobar la conexión y la detección. El usuario indicó que el módem era la única vía de conexión; esa condición no se verificó de forma independiente.  
**Entorno/enlace:** PC → ZeroTier → host `blueos` en `10.133.182.55`.  
**Versión Git:** `621a432`; había cambios locales previos en `AGENTS.md`, `README.md`, `docs/historial/2026-10-16-integracion.md` y `software/conectividad/README.md`.  
**Configuración antes/después:** no se modificó configuración ni estado del vehículo. No se abrió ningún puerto serie ni se consultó SIM o PIN.

## Resultado

`lsusb` identificó `19d1:0001 BYD EigenComm Compo`, correspondiente al Air780EG documentado. `eth1` estaba presente con `192.168.10.2/24`, y la ruta predeterminada apuntaba a `192.168.10.1` por `eth1`. `eth0` estaba sin portadora y `wlan0` sin portadora. Se listaron `/dev/ttyACM0` a `/dev/ttyACM3`; esta lectura no atribuye esos puertos a funciones concretas.

La comprobación confirma detección USB e interfaz/ruta móvil presentes en ese momento. No valida estado de la SIM, registro móvil, ZeroTier `ONLINE`, acceso completo, heartbeat ni arranque automático después de un ciclo de apagado/encendido. El ensayo de dos arranques de [la guía de conectividad](../../software/conectividad/README.md#ensayo-de-arranque-4g) sigue pendiente.

**Evidencia local privada:** `local/registros/F1-4G-DETECCION-20261020-01/lectura-ssh.txt`, SHA-256 `2761B76E6B57B4D30CA4D751878795BFDF89FC485F9795E952B9164DACEFE787`.  
**Estado final/reversión:** lectura terminada; sin cambios que revertir.
