# SITL de Kame

Esta carpeta contiene un ArduRover simulado, un puente MAVLink2REST y dos borradores de misión para Cockpit. Es el primer entorno de trabajo previsto antes de ensayar con el vehículo real.

## Archivos

- `start.sh`: inicia `mavlink2rest` en `127.0.0.1:8088` y ArduRover con modelo `motorboat-skid`, velocidad de simulación 1 y posición inicial `43.340080,-8.384526`.
- `virtual-params.parm`: parámetros adicionales cargados al iniciar el simulador.
- `generate_missions.py`: genera las dos misiones `.cmp` de `misiones/` alrededor de la posición inicial.
- `bin/ardurover` y `bin/mavlink2rest`: binarios usados por `start.sh`.
- `state/`: directorio de trabajo del simulador. El script usa `--wipe`, que reinicia los parámetros persistidos de SITL en cada arranque.

## Arranque

`start.sh` es un script Bash para un entorno Linux compatible. Necesita los binarios ejecutables de `bin/` y el árbol de fuentes de ArduPilot, por defecto en `$HOME/ardupilot`, para cargar `rover.parm`, `motorboat.parm` y `rover-skid.parm`. Se puede indicar otra ubicación mediante `ARDUPILOT_DIR`.

```bash
cd sitl
ARDUPILOT_DIR=/ruta/a/ardupilot bash ./start.sh
```

El puente escucha MAVLink en UDP `127.0.0.1:14550` y sirve MAVLink2REST en `127.0.0.1:8088`. Ctrl+C cierra el simulador y el script detiene el puente que inició. El archivo `bin/Cockpit-win-x64-1.18.4.exe` está presente, pero `start.sh` no lo ejecuta ni configura Cockpit automáticamente.

Desde `sitl/`, para regenerar los borradores de misión se necesita Python 3:

```bash
python3 generate_missions.py
```

El generador sobrescribe `misiones/01_ida_y_vuelta.cmp` y `misiones/02_triangulo.cmp`. Importarlas o ejecutarlas desde Cockpit requiere configurar ese cliente por separado; este README no presupone una conexión ya preparada.
