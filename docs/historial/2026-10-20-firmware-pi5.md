# Adecuación del firmware de Kame a Raspberry Pi 5 — 2026-10-20

**ID:** `F1-FIRMWARE-PI5-20261020-213454`. Auditoría desde las 21:34 CEST, Europe/Madrid, solicitada por el usuario para analizar y documentar si el firmware corresponde al vehículo y a Raspberry Pi 5. Alcance: lecturas del vehículo, contraste con fuentes oficiales y documentación local; sin instalación, cambios de parámetros, reinicios, armado ni órdenes PWM.

## Dictamen

**ArduRover y el destino Navigator64 son adecuados para el tipo de vehículo y la arquitectura del sistema. El ejecutable es el oficial estable 4.7.2, pero no resulta funcionalmente adecuado para la propulsión de esta instalación Pi 5 sin corregir su selección del bus PWM.** No se ha demostrado una elección equivocada de familia, un binario de otra arquitectura, una descarga corrupta o una modificación local del ejecutable.

| Aspecto | Veredicto y fundamento |
| --- | --- |
| Barco de superficie | ArduRover es la familia adecuada; `FRAME_CLASS=2` selecciona Boat. |
| Propulsión diferencial | `FRAME_TYPE=0`, `SERVO1_FUNCTION=73` y `SERVO3_FUNCTION=74` corresponden a control izquierdo/derecho; PWM normal (`MOT_PWM_TYPE=0`). La conexión izquierda física sigue pendiente de confirmar. |
| Arquitectura | El sistema es `aarch64` y el ejecutable es ELF64 AArch64. La plataforma seleccionada es `navigator64`. |
| Versión/procedencia del artefacto | 4.7.2 STABLE, idéntico por SHA-256 al binario oficial consultado. Es también la versión publicada en el directorio estable al realizar esta auditoría. |
| Acceso PWM en Pi 5 | Inadecuado en el binario actual: ArduPilot usa `i2c-4`; el PCA9685 de esta instalación está en `i2c-3`. El problema está observado, no es solo una posibilidad del código. |
| Validación del vehículo completo | Pendiente. Un binario oficial y un heartbeat correcto no validan motores, cableado, calibraciones, seguridad o navegación física. |

## Identidad y configuración verificadas

Lecturas frescas de la API de BlueOS/MAVLink2REST y del archivo ejecutable por SSH:

| Elemento | Resultado |
| --- | --- |
| Vehículo declarado por la API | `ArduRover`. |
| Placa | `Navigator64`, fabricante Blue Robotics, plataforma `navigator64`. |
| Firmware | 4.7.2 STABLE; commit `fb773567896014da007bca58358704d4a0d8516f`. |
| Ejecutable | 3 993 824 bytes; ELF clase 2, máquina 183: ELF64 AArch64. |
| SHA-256, instalado y oficial | `e0cede800da4bd895ec3d60f2d4ea68879e16f6da6998716440f8dded5ed736e`. |
| Sistema observado | Raspberry Pi 5 Model B Rev 1.1; kernel `6.6.31+rpt-rpi-2712`; imagen BlueOS `bluerobotics/blueos-core:1.4.3`. |
| Parámetros frescos | `FRAME_CLASS=2`, `FRAME_TYPE=0`, `SERVO1_FUNCTION=73`, `SERVO3_FUNCTION=74`, `MOT_PWM_TYPE=0`. |

El archivo oficial se descargó únicamente al PC, dentro de `local/`, para calcular su hash. No se instaló ni se ejecutó en el barco. La coincidencia identifica el artefacto, pero no determina quién lo instaló ni cuándo; el historial conserva referencias anteriores a 4.6.3 sin una trazabilidad completa de la transición.

## Adecuación al barco y significado de Navigator64

La [documentación oficial de barcos](https://ardupilot.org/rover/docs/boat-configuration.html) prescribe Rover con `FRAME_CLASS=2` para embarcaciones de superficie, e incluye propulsores Blue Robotics entre los motores admitidos. Las funciones izquierda/derecha 73/74 coinciden con el [control diferencial documentado](https://ardupilot.org/rover/docs/rover-motor-and-servo-connections.html). Estos datos respaldan la familia elegida; no acreditan ajuste de navegación ni respuesta física.

`navigator64` **no identifica una versión exclusiva para Pi 5**. Su [definición de hardware en el commit instalado](https://github.com/ArduPilot/ardupilot/blob/fb773567896014da007bca58358704d4a0d8516f/libraries/AP_HAL_Linux/hwdef/navigator64/hwdef.dat) reutiliza la definición Navigator y selecciona el compilador AArch64. BlueOS también decide el nombre Navigator64 por arquitectura del sistema, por lo que el sufijo no garantiza una adaptación completa de todos los periféricos a Pi 5.

## Problema concreto de compatibilidad

El [detector de Navigator de BlueOS 1.4.3](https://github.com/bluerobotics/BlueOS/blob/1.4.3/core/services/ardupilot_manager/flight_controller_detector/linux/navigator.py) distingue explícitamente ambos modelos: Pi 5 espera el PCA9685 en dirección `0x40`, bus 3; Pi 4 lo espera en bus 4. Se comprobó la misma asignación en el código instalado de BlueOS. Esto apoya que el bus 3 observado no sea una elección arbitraria de los parámetros de motor.

En cambio, el [controlador del commit de ArduRover instalado](https://github.com/ArduPilot/ardupilot/blob/fb773567896014da007bca58358704d4a0d8516f/libraries/AP_HAL_Linux/HAL_Linux_Class.cpp) construye la salida Navigator con el bus 4 fijo. En la [inspección directa previa](2026-10-20-pwm3-controlador.md) se observaron el descriptor abierto a ese bus y errores de lectura en la dirección del chip, mientras el dispositivo respondía en bus 3 sobre GPIO6/7. Allí estaba en reposo (`SLEEP`) y PWM3 tenía `FULL_OFF`; no había quedado programado el neutro que reportaba MAVLink.

Por tanto, el fallo localizado es una discordancia entre el controlador PWM oficial y la disposición Pi 5 que BlueOS reconoce. Es suficiente para explicar la ausencia de inicialización del ESC y requiere corregir esa comunicación antes de validar propulsión. No excluye otros problemas que puedan aparecer después. El error GPIO de la biblioteca antigua de [WebAssistant](2026-10-20-pwm3-webassistant.md) es independiente y no demuestra que la familia ArduRover sea incorrecta.

## Recomendación y límites

- Mantener la familia ArduRover, Boat y la arquitectura Navigator64; preparar una corrección verificable de la selección de bus según Pi 4/Pi 5. No se propone cambiar globalmente los números de bus para acomodar a ciegas el firmware.
- Reinstalar el mismo ejecutable oficial repetiría el código identificado. Tampoco se justifica volver a 4.6.3: su [controlador Navigator](https://github.com/ArduPilot/ardupilot/blob/Rover-4.6.3/libraries/AP_HAL_Linux/HAL_Linux_Class.cpp) también fija el bus 4. El código `master` consultado el 2026-10-20 conservaba esa selección; no se ha acreditado aquí una versión alternativa lista para instalar que resuelva el caso.
- Antes de una futura instalación, conservar el respaldo y el ejecutable original, identificar fuente/commit/hash del candidato y comprobar su acceso a Pi 5. Tras instalar con autorización, verificar comunicación con el chip, salida del estado de reposo, frecuencia/neutro y reconocimiento del ESC, inicialmente sin ordenar giro. Corregir el bus es necesario, pero no equivale a validar todo el vehículo.
- La revisión física exacta de la PCB, todos los sensores, el cableado de ambos lados y las prestaciones en agua no se verificaron en esta auditoría. El estado de la MMC5983 procede de la comunicación del usuario y no de una nueva inspección del montaje.

## Fuentes, evidencias y estado final

La versión estable y el commit se contrastaron directamente con los archivos oficiales [stable/git-version.txt](https://firmware.ardupilot.org/Rover/stable/navigator64/git-version.txt), [4.7.2/git-version.txt](https://firmware.ardupilot.org/Rover/stable-4.7.2/navigator64/git-version.txt) y el [ejecutable 4.7.2](https://firmware.ardupilot.org/Rover/stable-4.7.2/navigator64/ardurover), consultados el 2026-10-20. La consulta de catálogo de la API local no devolvió datos; por eso el contraste de versión se realizó con el servidor oficial, sin modificar el catálogo local.

Datos crudos y copias de fuentes bajo `local/registros/F1-FIRMWARE-PI5-20261020-213454/`: identidad instalada, binario oficial, versión/placa y parámetros frescos, código del detector instalado, comparación, fuentes consultadas y `SHA256.json`. El commit del repositorio y los cambios locales preexistentes se registran en `audit.json`. No se cambiaron de rama ni se publicaron cambios.

**En repositorio:** informe y actualización del inventario/estado. **En el vehículo:** firmware y configuración conservados, ArduPilot funcionando y desarmado en la lectura final. **Verificado en ejecución:** identidad, arquitectura, parámetros y estado del autopiloto; la discordancia PWM queda respaldada por las lecturas previas enlazadas. **Pendiente:** corrección del controlador y validación física del neutro/propulsión. No hay cambios operativos que revertir en esta auditoría.

Comprobaciones locales: `python3 .github/checks/check_repository.py` con Python 3.12.14 pasó la revisión de sintaxis/configuración, enlaces/anclas, patrones de secretos, generación de misiones y visor; `git diff --check` de los documentos afectados no señaló errores. Son comprobaciones del repositorio, no una validación eléctrica o de navegación del barco.
