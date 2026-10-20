# Visor 3D del Navigator

Pequeño servidor HTTP local que lee telemetría de BlueOS y muestra una figura 3D orientada con la actitud (`ATTITUDE`) que publica el autopiloto. También presenta aceleración y giroscopio (`RAW_IMU`), vibración, recortes del acelerómetro, estado del EKF, brújula, GPS y armado.

## Uso

Requiere Node.js 20 o posterior. Desde PowerShell, en la raíz del proyecto:

```powershell
node software/visor/server.mjs
```

Abre [http://127.0.0.1:8765](http://127.0.0.1:8765). El selector permite elegir BlueOS por Wi-Fi (`192.168.42.1`) o Ethernet (`192.168.2.2`). Para cerrar el servidor, pulsa Ctrl+C en PowerShell.

El servidor solo escucha en `127.0.0.1` y hace solicitudes HTTP GET a MAVLink2REST. No cambia parámetros ni envía mensajes o comandos al vehículo. La figura representa la estimación de actitud que publica ArduPilot; es una visualización para inspección y no certifica que la IMU o la calibración estén bien.

## Comprobación local y límites

Desde la raíz, `python .github/checks/check_repository.py` arranca el visor con telemetría simulada y verifica su página, API, eventos SSE, cambio de origen y cierre con una conexión SSE abierta, sin consultar BlueOS. Ctrl+C o SIGTERM detienen las consultas y cierran las conexiones HTTP/SSE del servidor. En uso normal el servidor sí consulta el vehículo. El indicador conectado depende de la frescura de `ATTITUDE`; GPS y armado no tienen todavía comprobación independiente de antigüedad. Esta limitación sigue pendiente y no se considera corregida por la migración.
