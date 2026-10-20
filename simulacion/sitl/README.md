# SITL de Kame

ArduRover simulado con modelo `motorboat-skid`, velocidad de simulación 1 y origen `43.340080,-8.384526,0,270`. Sirve para ensayar navegación antes del vehículo real; las fases están en el [plan](../../docs/plan.md).

## Requisitos y recursos

Linux x86_64 con Bash y los binarios ejecutables `local/bin/sitl/ardurover` y `local/bin/sitl/mavlink2rest`, desde la raíz. Se preservaron los binarios existentes; su versión/build y origen de descarga no se han confirmado. Comparar sus hashes con el [inventario](../../docs/historial/recursos.json). En un clon limpio hay que recuperarlos del respaldo privado o preparar binarios compatibles y documentar su procedencia antes de ejecutar.

El árbol de ArduPilot se busca en `$HOME/ardupilot` y debe contener `Tools/autotest/default_params/rover.parm`, `motorboat.parm` y `rover-skid.parm`. Se puede indicar otra ubicación con `ARDUPILOT_DIR`; registrar la revisión utilizada al repetir un ensayo.

## Arranque

Desde la raíz del repositorio en Bash/Linux, también desde Ubuntu de WSL:

```bash
bash simulacion/sitl/start.sh
# Otra ubicación del árbol de ArduPilot:
ARDUPILOT_DIR=/ruta/a/ardupilot bash simulacion/sitl/start.sh
```

El script busca sus recursos por ubicación del proyecto, independientemente del directorio de trabajo. En WSL el proyecto puede estar bajo `/mnt/c/`; si otro sistema no conserva el permiso ejecutable de los binarios recuperados, aplicar `chmod +x` solo a esos archivos locales.

El puente usa UDP `127.0.0.1:14550` y HTTP MAVLink2REST `127.0.0.1:8088`. Deben estar libres antes de arrancar. El script no conecta al barco, no abre Cockpit y detiene los procesos que inició al salir, recibir Ctrl+C o SIGTERM. Cockpit se configura por separado contra el puente local. El instalador Windows original permanece en `local/bin/sitl/Cockpit-win-x64-1.18.4.exe`.

`virtual-params.parm` conserva crucero/waypoints a 1,2 m/s, sin viento ni olas. El estado y los logs se generan bajo `local/estado/sitl/`. **Cada arranque utiliza `--wipe` y reinicia los parámetros persistidos.** El EEPROM anterior se conserva separado en `local/estado/sitl-original/`.

## Misiones y comprobación

Los dos borradores `.cmp` y su generador están en [misiones](../../misiones/README.md). Para validar sintaxis, enlaces, generación y visor simulado, desde la raíz:

```bash
python3 .github/checks/check_repository.py
python3 .github/checks/check_sitl.py
```

La segunda comprobación requiere Linux, binarios locales y defaults de ArduPilot. Arranca una sesión corta solo en loopback, verifica heartbeat fresco y desarmado y comprueba que no queden sus procesos ni puertos ocupados. No se ejecuta automáticamente en CI, donde esos binarios no se distribuyen.
