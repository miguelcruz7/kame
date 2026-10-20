# Trabajar en Kame

## Orden de lectura

1. [Estado observado y siguiente trabajo](docs/estado.md).
2. [Plan de cinco fases](docs/plan.md), empezando por la fase activa.
3. [Hardware](docs/hardware.md), [preparación](docs/preparacion.md) y README del componente afectado.

La fase actual es preparar y validar el barco. SITL permite ensayar cambios de navegación; Gazebo y ROS 2 se incorporarán en su fase. Las observaciones fechadas son históricas hasta volver a verificarse.

## Flujo de trabajo

Trabajar con una tarea de objetivo concreto, alcance y criterios de aceptación. Seguir: tarea → rama → cambio → comprobaciones → revisión → resultado registrado. Hasta disponer de GitHub, el siguiente trabajo se mantiene en `docs/estado.md`; después se enlazan los issues desde ese documento.

- Mantener código, configuración y README juntos en su componente. Evitar documentación duplicada y carpetas para funcionalidades aún no implementadas.
- Separar organización y cambios funcionales. Los traslados locales no cambian las rutas instaladas en la Raspberry.
- Antes de entregar, ejecutar desde la raíz `python .github/checks/check_repository.py`. Usa Python 3.12+, Node.js 20+ y Git, sin paquetes de percepción ni acceso al vehículo. En Linux comprueba también sintaxis Bash.
- Para cambios de navegación o del arranque SITL, ejecutar además `python3 .github/checks/check_sitl.py` en Linux/WSL con los recursos descritos en su README. Esta comprobación usa únicamente loopback.
- Registrar qué se verificó, su resultado y límites. Una comprobación sintáctica no valida calibración ni funcionamiento físico.

## Inspección del vehículo

Elegir un enlace de la [tabla de redes](docs/hardware.md#red-y-puertos). Empezar por consultas de solo lectura: heartbeat fresco, armado, `GPS_RAW_INT` (fix, satélites y coordenadas), avisos prearm/brújula y cámara/vídeo. Registrar fecha, enlace, fuente de cada lectura y lo que no pudo comprobarse.

Priorizar API documentada de la versión instalada de BlueOS, MAVLink/MAVLink2REST o SSH. Usar la interfaz cuando aporte evidencia visual o una función sin API fiable. HTTP 200 no demuestra telemetría; RTSP o una fuente anunciada no demuestran WebRTC actual y fluido dentro de Cockpit.

## Límites de actuación

No cambiar parámetros, firmware o asignaciones de puerto, ni reiniciar, armar o accionar motores sin autorización explícita y comprobación de seguridad. Mantener el barco desarmado mientras existan avisos de brújula o no se haya validado el GPS. Las autorizaciones históricas no acreditan las condiciones físicas de una nueva sesión.

Antes de un cambio autorizado, guardar el valor o configuración vigente, aplicar solo lo acordado, leer el resultado y registrar valor anterior, nuevo, fecha, comprobaciones y reversión. Leer los procedimientos de [vídeo](software/video/README.md) o [conectividad](software/conectividad/README.md) antes de intervenir. Conservar la cámara original `/cam` cuando se trabaje en YOLO.

## Credenciales y recursos privados

Las credenciales operativas están en `local/credenciales.md`, excluido de Git. Leerlas únicamente cuando sean necesarias; no copiarlas a Markdown versionado, salida de comandos, issues o PR. Mantenerlas ahí si cambian. No publicar tokens locales, claves ni identidades de red.

El PIN instalado permanece en `/etc/kame/air780eg-pin`. El temporizador Air780EG solo debe intentarlo cuando la SIM indique `SIM PIN`; si hay un intento sin confirmar, comprobar su estado antes de repetirlo. `/dev/ttyACM1` era el puerto AT y `/dev/ttyACM0` el GPS: verificar identidad antes de abrir un dispositivo y no competir por el puerto que usa ArduPilot.

Mantener binarios, modelos, wheels, cachés y registros pesados en `local/`. Sus originales y procedencia están en el [inventario](docs/historial/recursos.json). No eliminar archivos únicos durante una limpieza.

## Registro de trabajo

Actualizar [estado.md](docs/estado.md) con observaciones verificables y el siguiente trabajo; conservar mediciones extensas en el [historial](docs/historial/README.md). Un ensayo registra ID, fecha/zona horaria, objetivo, entorno, versión Git y cambios locales, configuración antes/después, autorización cuando proceda, resultado, evidencias y estado final. Los archivos crudos se conservan en `local/registros/<ID>/` o en un archivo privado recuperable, con ubicación y hash anotados.

Los fallos pendientes del visor, YOLO o el vehículo se corrigen en tareas específicas; no se consideran resueltos por reorganizar el repositorio.
