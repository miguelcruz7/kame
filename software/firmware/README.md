# Firmware de Navigator64 para Raspberry Pi 5

Este componente conserva una corrección local de ArduRover 4.7.2: elegir el bus I²C 3 del PCA9685 cuando ArduPilot detecta Pi 5, conservando el bus 4 para las demás plataformas. No cambia canales, parámetros, GPIO26, frecuencia ni conversión de pulsos. La selección se realiza en la construcción de la salida Navigator, después de inicializar `UtilRPI`.

Base exacta: `fb773567896014da007bca58358704d4a0d8516f`. El parche modifica solo `libraries/AP_HAL_Linux/HAL_Linux_Class.cpp` de ArduPilot. Es una compilación local; el texto de versión 4.7.2 no la convierte en el binario oficial. Consultar [estado del barco](../../docs/estado.md) para distinguir preparación, instalación y verificación física.

**Resultado del 2026-10-20:** binario `5cf0eb0ddc6fafc378862883614948dfc5f90f9e63bf4fd1e8ff5cdd6ca6a537` instalado por la API de BlueOS y verificado tras la instalación, tras reiniciar únicamente ArduPilot y tras un apagado/encendido realizado por el usuario. El ESC de PWM3 reconoció el neutro sin movimiento, según el usuario; se decodificaron diez fotogramas locales de cámara manteniendo su bus 4. El 2026-10-21 el usuario comunicó que ya funcionan los motores, sin aportar aún datos individuales de la prueba. Ver [registro de intervención y reversión](../../docs/historial/2026-10-20-pwm-pi5-reparacion.md).

## Compilar en el PC

Se necesita Ubuntu/WSL x86_64, Git, Python 3.10 con `venv`, GCC/G++ 11 para `aarch64-linux-gnu` y sus bibliotecas de desarrollo. La compilación nunca conecta con el vehículo. Desde la raíz:

```bash
python3 software/firmware/build.py --jobs 8
```

El programa fija el commit, verifica que el único cambio de fuente sea el parche exacto, inicializa los submódulos en sus commits y crea un entorno virtual con las dependencias fijadas. Usa `waf configure --board navigator64 --toolchain aarch64-linux-gnu` y `waf rover`. Rechaza modificaciones ajenas en el clon. No cambia la rama del repositorio Kame ni instala paquetes en la Raspberry.

Fuente, entorno y compilación quedan en `local/firmware/`; el ejecutable y `manifest.json` en `local/firmware/artifacts/navigator64-pi5-pwm/`. El manifiesto registra base, parche, fuente modificada, submódulos, versiones, opciones, paquetes del compilador y SHA-256. Guardar también la salida de compilación. El manifiesto identifica la receta y resultado; no promete igualdad binaria entre máquinas o versiones de herramientas distintas.

En WSL conviene que `local/firmware` enlace a una carpeta del sistema Linux para evitar la lentitud de NTFS. El programa resuelve ese enlace antes de ejecutar las herramientas. Preservar los recursos existentes y detener sus procesos de compilación/descarga antes de trasladarlos; el entorno virtual debe usar la versión de Python documentada. Las dependencias Python, incluido `pexpect`, están fijadas en `requirements-build.txt`.

El compilador puede estar instalado en el PC o extraído sin privilegios en `local/firmware/toolchain/root/`; esta ubicación tiene prioridad. En Ubuntu 22.04, se puede usar `apt-get download` de los paquetes `gcc-11-aarch64-linux-gnu`, `g++-11-aarch64-linux-gnu`, `cpp-11-aarch64-linux-gnu`, `binutils-aarch64-linux-gnu` y sus dependencias, y extraerlos con `dpkg-deb -x`. Conservar los `.deb`, sus versiones y hashes. Crear los enlaces locales sin sufijo `-11` para GCC/G++ si el paquete no los incluye. No hace falta modificar `/usr` ni ejecutar la compilación con `sudo`.

Para esos paquetes extraídos, la receta añade las bibliotecas de herramientas de `root/usr/lib/x86_64-linux-gnu` a `LD_LIBRARY_PATH` y `--sysroot=<root>` a compilación/enlace. Esto permite localizar las bibliotecas ARM referidas con rutas absolutas por los scripts del enlazador, sin instalar paquetes en el sistema. Estos ajustes quedan registrados en el manifiesto.

Antes de instalar, comprobar ELF64 AArch64, intérprete, bibliotecas y versiones de símbolos requeridas frente al contenedor BlueOS instalado. Registrar el resultado de `readelf`; no dar por compatible un binario solo porque compile.

## Instalar y verificar

La instalación requiere autorización de la sesión y comprobación física según [preparación](../../docs/preparacion.md). Mantener todos los controles de ESC retirados, vehículo desarmado y WebAssistant deshabilitado. Respaldar ejecutable, parámetros completos, configuración y registros del chip antes del cambio.

En BlueOS 1.4.3, usar `POST /ardupilot-manager/v1.0/install_firmware_from_file?board_name=Navigator64`, multipart con campo `binary`, sin `parameters`. En la intervención documentada se subió el ejecutable compilado una sola vez y la API respondió HTTP 200; se contrastó después el hash del archivo y del proceso. La API detiene y arranca ArduPilot también al salir por error. Ante respuesta perdida, verificar hash y proceso antes de repetir. No usar la instalación para cambiar valores predeterminados ni placa.

Verificar hash del proceso instalado, heartbeat fresco y desarmado, parámetros conservados, descriptor `/dev/i2c-3` y registros del PCA9685: reloj externo, autoincremento, sin `SLEEP`, prescaler 119. PWM3 a 1500 µs en MAVLink debe corresponder aproximadamente a 306 cuentas (1494 µs) por la conversión existente del controlador; las 307 cuentas del ensayo directo no son el valor esperado aquí. Repetir tras reiniciar ArduPilot con controles aislados.

Solo después, conectar exclusivamente el control del T200 durante un máximo de diez segundos bajo supervisión y retirarlo al acabar. Registrar señal/neutro reconocidos y ausencia de movimiento; no armar ni ordenar giro. Detener ArduPilot no garantiza borrar el último PWM. Si se pierde la conexión, retirar control o cortar potencia.

## Reversión y límites

Con controles aislados, detener ArduPilot y verificar proceso terminado antes de escribir directamente en el chip. Apagar mediante `FULL_OFF` y `SLEEP`, restaurar el ejecutable respaldado por la API y comprobar heartbeat desarmado. No borrar almacenamiento ni restaurar valores automáticos antiguos de sensores o estadísticas. Si no se recupera, mantener los controles aislados y documentar el bloqueo.

`RESTART` es un bit de estado: no comparar `MODE1` como un byte de configuración ordinario. `EXTCLK` permanece seleccionado hasta retirar alimentación del chip o ejecutar un reset; no enviar un reset general al bus para intentar restaurar ese bit. La lectura posterior al apagado y encendido del usuario acreditó que el parche persistía y volvía a generar neutro en ese ciclo. La prueba de neutro no documenta giro por lado, navegación ni estabilidad de 4G. Una actualización posterior de firmware puede sustituir la compilación local: comprobar identidad antes de atribuirle esta corrección.
