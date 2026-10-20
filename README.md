# Kame

Vehículo de superficie con Raspberry Pi 5, BlueOS, Navigator64 y ArduRover. Integra navegación por waypoints, cámara IMX462, vídeo YOLO en Cockpit y acceso móvil.

**Fase actual: 1 — preparación y validación del barco.** La última observación del vehículo es del 2026-10-19; el estado físico debe comprobarse de nuevo antes de operar. La reorganización local no es una inspección del barco.

## Por dónde empezar

1. Leer [AGENTS.md](AGENTS.md) para trabajar con el proyecto.
2. Consultar [estado y siguiente trabajo](docs/estado.md).
3. Revisar [las cinco fases](docs/plan.md) y [la preparación del barco](docs/preparacion.md).
4. Abrir el README del componente afectado.

```text
kame/
├── README.md / AGENTS.md     Entrada y reglas de trabajo
├── docs/                    Plan, estado, hardware, preparación e historial
├── software/
│   ├── video/               Cámara, YOLO, servicios y diagnóstico
│   ├── conectividad/        Air780EG y ZeroTier
│   └── visor/               Visor de telemetría del Navigator
├── simulacion/sitl/         ArduRover simulado y puente MAVLink2REST
├── misiones/                Borradores de misión y generador
├── local/                   Recursos privados y pesados; ignorado por Git
└── .github/                 Comprobaciones y plantillas de trabajo
```

## Componentes y comandos

Ejecutar desde la raíz:

| Necesidad | Guía | Comando |
| --- | --- | --- |
| Hardware, puertos y redes | [Hardware](docs/hardware.md) | Consulta documental |
| BlueOS, firmware y sensores | [Preparación](docs/preparacion.md) | Procedimientos sujetos a autorización |
| Cámara y detección visual | [Vídeo](software/video/README.md) | Servicios instalados en la Pi |
| Red móvil | [Conectividad](software/conectividad/README.md) | Diagnóstico en su guía |
| Visor local | [Visor](software/visor/README.md) | `node software/visor/server.mjs` |
| Simulador Linux/WSL | [SITL](simulacion/sitl/README.md) | `bash simulacion/sitl/start.sh` |
| Generar misiones | [Misiones](misiones/README.md) | `python misiones/generate_missions.py` |
| Comprobar sin barco | [Entrega](AGENTS.md#flujo-de-trabajo) | `python .github/checks/check_repository.py` |

El visor escucha en `http://127.0.0.1:8765` y consulta BlueOS al ejecutarlo normalmente. Las comprobaciones automáticas usan telemetría simulada. YOLO sigue siendo apoyo visual experimental; no está validado para controlar navegación ni motores.

## Recursos locales y Git

El código y la documentación están en Git. `local/` contiene credenciales, ejecutables SITL/Cockpit, wheels, modelos y registros originales. Un clon limpio necesita recuperar esos recursos para ejecutar SITL o instalar YOLO; nombres, hashes y procedencia conocida están en el [inventario](docs/historial/recursos.json). Una procedencia pendiente no se presenta como descarga reproducible.

Las credenciales se conservan exclusivamente en `local/credenciales.md`; leerlas solo cuando una tarea autorizada las necesite y evitar mostrarlas. El PIN instalado sigue en `/etc/kame/air780eg-pin`.

GitHub y la licencia se decidirán antes de publicar. Las coordenadas e IP históricas se conservan como datos técnicos; se revisarán antes de hacer público el repositorio. El [historial](docs/historial/README.md) conserva las pruebas y la [migración](docs/historial/2026-10-20-reestructuracion.md) describe el respaldo y las verificaciones locales.
