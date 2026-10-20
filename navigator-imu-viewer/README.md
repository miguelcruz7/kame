# Visor 3D del Navigator

Pequeño servidor HTTP local que lee telemetría de BlueOS y muestra una figura 3D orientada con la actitud (`ATTITUDE`) que publica el autopiloto. También presenta aceleración y giroscopio (`RAW_IMU`), vibración, recortes del acelerómetro, estado del EKF, brújula, GPS y armado.

## Uso

Requiere Node.js 20 o posterior. Desde PowerShell:

```powershell
cd "C:\Users\Miguel\Desktop\troyan drones\programas\kame\navigator-imu-viewer"
node .\server.mjs
```

Abre [http://127.0.0.1:8765](http://127.0.0.1:8765). El selector permite elegir BlueOS por Wi-Fi (`192.168.42.1`) o Ethernet (`192.168.2.2`). Para cerrar el servidor, pulsa Ctrl+C en PowerShell.

El servidor solo escucha en `127.0.0.1` y hace solicitudes HTTP GET a MAVLink2REST. No cambia parámetros ni envía mensajes o comandos al vehículo. La figura representa la estimación de actitud que publica ArduPilot; es una visualización para inspección y no certifica que la IMU o la calibración estén bien.
