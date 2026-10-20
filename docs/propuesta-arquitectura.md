# Propuesta de arquitectura y flujo de trabajo de Kame

Fecha: 2026-10-20, Europe/Madrid. Estado: **propuesta para revisión**.

Este documento define la estructura de destino y la migración del proyecto actual. Las rutas del árbol son propuestas; todavía no se han trasladado archivos ni creado integraciones con GitHub. La última evidencia del vehículo sigue en [estado.md](estado.md). Esta revisión no incluye una conexión al barco.

## 1. Decisión principal

Mantener **un único repositorio organizado por responsabilidades técnicas**, con una hoja de ruta de cinco fases y criterios de salida verificables. El código de percepción, comunicaciones o navegación vive en su subsistema y se reutiliza entre fases. Las fases organizan los objetivos y la validación.

El proyecto persigue esta secuencia, definida por el usuario:

1. Preparar el barco: BlueOS, firmware, integración, calibración y comprobación de sensores y propulsión.
2. Navegar por waypoints y ajustar el comportamiento de los motores y del control.
3. Incorporar evasión de obstáculos con programas Python sencillos y supervisados.
4. Construir el modelo en Gazebo e integrar ROS 2 para desarrollar autonomía avanzada en simulación.
5. Transferir y validar esa autonomía con ROS 2 en el barco real, en el agua.

**La fase actual es la 1.** La instrucción anterior de situar SITL como primera fase debe actualizarse durante la migración. SITL queda como herramienta de ensayo desde las fases tempranas y como comprobación previa a los cambios de navegación. Gazebo y ROS 2 se desarrollan en la fase 4.

La recomendación de consolidar primero el funcionamiento manual y autónomo de ArduPilot antes de añadir ROS coincide con la [guía oficial de ArduPilot sobre ROS 2](https://ardupilot.org/dev/docs/ros2.html).

## 2. Principios de organización

- Carpetas y nombres técnicos en inglés; documentación explicativa en español. Los nombres de parámetros y herramientas conservan su forma original.
- Cada dato tiene un documento responsable: estado, objetivos, inventario, procedimiento, decisión o evidencia.
- Los README permiten encontrar y ejecutar el trabajo de su área. Los AGENTS definen cómo puede trabajar un agente en ella.
- Los componentes futuros se marcan como planificados. Sus paquetes y carpetas de implementación se crean al empezar la fase correspondiente.
- Una versión observada, un respaldo y una configuración aprobada son estados diferentes y se registran como tales.
- Ninguna observación histórica certifica el estado presente del barco. Una prueba de software tampoco certifica un resultado físico.
- Los experimentos tienen identificador, versión del código, configuración, resultado y evidencia recuperable.
- La migración de rutas se realiza por separado de los cambios funcionales para poder revisar qué se movió y qué cambió.

## 3. Árbol de destino

El árbol muestra la arquitectura completa prevista. Las entradas marcadas con `[F3]` o `[F4]` se incorporan cuando comience esa fase. No es una instrucción para crear ahora carpetas vacías.

```text
kame/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE                         # Elegir con el propietario antes de publicar
├── .gitignore
├── .gitattributes
├── .editorconfig
├── .env.example                    # Nombres y ejemplos sin credenciales reales
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── task.yml
│   │   ├── defect.yml
│   │   └── field-test.yml
│   ├── pull_request_template.md
│   └── workflows/
│       ├── quality.yml
│       ├── sitl.yml                # Al disponer de un ensayo repetible
│       └── ros2.yml                # [F4]
│
├── docs/
│   ├── README.md                   # Índice por necesidad del lector
│   ├── status.md                   # Fase activa, última evidencia y bloqueos
│   ├── roadmap/
│   │   ├── README.md
│   │   ├── 01-commissioning.md
│   │   ├── 02-waypoint-navigation.md
│   │   ├── 03-python-avoidance.md
│   │   ├── 04-gazebo-ros2.md
│   │   └── 05-ros2-water-validation.md
│   ├── architecture/
│   │   ├── README.md
│   │   ├── interfaces.md
│   │   └── decisions/
│   │       └── README.md           # Índice de decisiones y su estado
│   ├── hardware/
│   │   ├── README.md
│   │   ├── inventory.md
│   │   ├── wiring.md
│   │   └── frames.md
│   ├── operations/
│   │   ├── README.md
│   │   ├── commissioning.md
│   │   ├── calibration.md
│   │   ├── propulsion.md
│   │   ├── preflight.md
│   │   ├── deployment.md
│   │   └── recovery.md
│   ├── development/
│   │   ├── README.md
│   │   ├── agent-workflow.md
│   │   ├── environments.md
│   │   ├── testing.md
│   │   └── artifacts.md
│   ├── history/
│   │   ├── README.md
│   │   └── YYYY-MM-DD-topic.md     # Historial existente conservado y fechado
│   ├── runs/
│   │   ├── README.md
│   │   └── RUN-ID/
│   │       ├── README.md           # Resultado resumido del ensayo
│   │       └── manifest.yaml       # Configuración y referencias a evidencia
│   └── templates/
│       ├── test-run.md
│       ├── incident.md
│       └── decision.md
│
├── vehicle/
│   ├── README.md
│   ├── AGENTS.md
│   ├── blueos/
│   │   └── README.md               # Instalación, versiones y ajustes reproducibles
│   ├── firmware/
│   │   ├── README.md
│   │   └── manifest.yaml           # Origen, versión, plataforma y hash verificados
│   ├── parameters/
│   │   ├── README.md
│   │   ├── snapshots/              # Lecturas fechadas, revisadas antes de publicar
│   │   └── baselines/              # Solo configuraciones aprobadas con evidencia
│   └── model/                      # [F4]
│       ├── README.md
│       ├── measurements.yaml       # Geometría, masa y propiedades conocidas
│       └── meshes/
│
├── software/
│   ├── README.md
│   ├── AGENTS.md
│   ├── perception/
│   │   ├── README.md
│   │   ├── yolo_stream.py
│   │   ├── config/
│   │   ├── systemd/
│   │   ├── diagnostics/
│   │   ├── models.yaml             # Procedencia y hashes de modelos
│   │   └── requirements.lock       # Dependencias validadas para su plataforma
│   ├── connectivity/
│   │   ├── README.md
│   │   ├── air780eg-unlock.py
│   │   ├── config/
│   │   └── systemd/
│   ├── telemetry-viewer/
│   │   ├── README.md
│   │   ├── server.mjs
│   │   └── public/
│   └── autonomy/                   # [F3]
│       ├── README.md
│       ├── pyproject.toml
│       └── src/kame_autonomy/
│           ├── contracts.py
│           ├── missions.py
│           ├── avoidance.py
│           ├── command_gate.py
│           └── adapters/
│               ├── mavlink.py
│               └── replay.py
│
├── missions/
│   ├── README.md
│   ├── waypoints/
│   │   ├── README.md
│   │   └── cockpit/*.cmp
│   ├── avoidance/                  # [F3]
│   │   └── README.md
│   └── tools/
│       └── generate_missions.py
│
├── simulation/
│   ├── README.md
│   ├── AGENTS.md
│   ├── sitl/
│   │   ├── README.md
│   │   ├── start.sh
│   │   ├── dependencies.lock.yaml
│   │   └── parameters/virtual.parm
│   └── gazebo/                     # [F4]
│       ├── README.md
│       ├── models/
│       ├── worlds/
│       ├── scenarios/
│       └── launch/
│
├── ros2/                           # [F4] Workspace colcon
│   ├── README.md
│   ├── AGENTS.md
│   ├── dependencies.repos          # Repositorios externos fijados a revisiones
│   └── src/
│       ├── kame_description/       # Descripción del robot y marcos
│       ├── kame_vehicle_interface/ # Adaptador con ArduPilot, transporte por decidir
│       ├── kame_navigation/        # Nodos que reutilizan la lógica Python
│       └── kame_bringup/           # Arranque y configuración por entorno
│
├── tests/
│   ├── README.md
│   ├── unit/
│   ├── integration/
│   ├── replay/
│   ├── simulation/
│   └── fixtures/                   # Ejemplos pequeños, revisados y sin secretos
│
├── tools/
│   ├── README.md
│   └── fetch_assets.py             # Descargas verificadas; sin despliegue al barco
│
├── artifacts/
│   ├── README.md                   # Este archivo y assets.yaml sí se versionan
│   ├── assets.yaml                # Origen, licencia, versión y hash de binarios
│   ├── cache/                     # Ignorado: binarios, wheels y modelos
│   └── runs/                      # Ignorado: logs, vídeo, rosbags y capturas crudas
│
└── local/                          # Ignorado: configuración privada de cada equipo
    ├── .env
    └── credentials.md
```

Los directorios de pruebas se crean a medida que aparecen comprobaciones útiles. El visor Node puede seguir sin dependencias externas; no necesita un manifiesto de dependencias ficticio. Los scripts de systemd y su configuración permanecen junto al componente que despliegan.

## 4. Qué explica cada Markdown

### Entrada para humanos y agentes

| Documento | Pregunta que responde | Límite de su contenido |
| --- | --- | --- |
| `README.md` | ¿Qué es Kame, en qué fase está y por dónde empiezo? | Breve presentación y enlaces a las fuentes responsables. |
| `AGENTS.md` | ¿Cómo debo trabajar en este repositorio y qué puedo ejecutar? | Reglas comunes, orden de lectura y límites de actuación. |
| `CONTRIBUTING.md` | ¿Cómo preparo, compruebo y entrego un cambio? | Flujo compartido por personas y agentes. |
| `SECURITY.md` | ¿Cómo se tratan accesos, secretos y problemas de seguridad? | Política publicable y vía de reporte pendiente de definir. |
| `docs/README.md` | ¿Dónde encuentro un procedimiento, un diseño o una prueba? | Índice por tareas del lector. |
| `docs/status.md` | ¿Qué se ha verificado, qué bloquea y cuál es la próxima tarea? | Síntesis fechada con enlaces a evidencias e issues. |
| `docs/roadmap/README.md` | ¿Cuál es la secuencia y el avance de las cinco fases? | Índice y estado; los criterios están en cada fase. |
| `docs/architecture/README.md` | ¿Cómo se conectan los componentes y quién controla qué? | Diseño aceptado; las decisiones propuestas se identifican como propuestas. |
| `docs/development/agent-workflow.md` | ¿Cómo ejecuta y entrega una tarea un agente? | Procedimiento reproducible, sin repetir las reglas de AGENTS. |

`context.md` se retira después de migrar sus decisiones e información útil a estas fuentes. La incorporación pasa a ser `README → AGENTS → status → documento de fase → README del subsistema`. Evitamos mantener otro resumen extenso que deba sincronizarse manualmente.

### Reglas de los documentos operativos

- `hardware/inventory.md`: equipo confirmado, equipo comunicado por el usuario y equipo pendiente de identificar, con fecha y fuente. Incluye ESC y motor por lado.
- `hardware/wiring.md`: conexiones, alimentación, masas, pines, dispositivos y puertos. Las asignaciones observadas llevan fecha.
- `hardware/frames.md`: proa, ejes del casco, montaje de sensores, unidades y transformaciones. Las conversiones NED/ENU y grados/radianes se documentan antes de integrar ROS 2.
- `operations/commissioning.md`: orden de puesta en servicio y enlaces a calibración y propulsión.
- `operations/calibration.md`: procedimientos de sensores, precondiciones y cómo registrar resultados. Los valores concretos de una sesión pertenecen a su registro.
- `operations/propulsion.md`: identificación y comprobación de ESC/motores, señal y respuesta por lado, con los límites operativos aplicables.
- `operations/preflight.md`: comprobaciones frescas para cada sesión y condiciones de interrupción.
- `operations/deployment.md`: preparación, lectura previa, aplicación autorizada, verificación y reversión.
- `operations/recovery.md`: recuperación de enlace, telemetría y servicios, diferenciando diagnóstico de acciones que requieren autorización.
- `development/environments.md`: Windows para herramientas compatibles, Linux para SITL y el entorno Linux validado que se elija para Gazebo/ROS 2. La plataforma real de la Raspberry se documenta aparte.
- `development/testing.md`: qué demuestra cada prueba y qué queda fuera de su alcance.
- `development/artifacts.md`: qué se versiona, qué se descarga y cómo se conserva y recupera evidencia.

### Contenido mínimo de cada fase

Cada `docs/roadmap/0N-*.md` utiliza la misma estructura:

1. Objetivo y alcance.
2. Condiciones de entrada.
3. Entregables técnicos y documentales.
4. Ensayos y métricas, con sus límites acordados antes de ejecutar.
5. Criterios de salida y evidencia exigida para cada uno.
6. Dependencias, bloqueos y decisiones abiertas.

Cada criterio tiene ID, estado, responsable de revisión y enlace al ensayo. Estados: `pendiente`, `en curso`, `verificado`, `fallido` o `no aplicable` con justificación. No se cierra una fase por porcentaje de tareas terminadas.

## 5. Fases y criterios de avance

### Fase 1: puesta en servicio del barco

**Entregables:** inventario y cableado confirmados; BlueOS y firmware identificados; configuración respaldada; parámetros observados separados de los aprobados; sensores integrados y calibrados; comunicaciones y propulsión comprobadas con supervisión.

**Criterios de salida:**

- Versiones y configuración recuperables, con procedimiento de reversión comprobado en el alcance acordado.
- GPS con fix y posición contrastados; actitud y rumbo coherentes con movimientos físicos; calibraciones registradas y condiciones prearm verificadas.
- ESC y motor de cada lado identificados; alimentación, señal, sentido y respuesta comprobados. El PWM reportado por el autopiloto se distingue del efecto medido en el actuador.
- Control manual, parada y recuperación del control comprobados en condiciones controladas.
- Enlace operativo estable durante la duración de ensayo definida; comportamiento ante pérdida de enlace y recuperación documentado.
- Vídeo actual dentro de Cockpit si se utilizará para supervisar la navegación. 4G se convierte en requisito de salida si el escenario de la fase 2 depende de él.
- Los incidentes de armado inesperado y pérdida de telemetría tienen disposición documentada: causa resuelta o medidas verificadas y decisión humana explícita sobre el ensayo permitido.

El estado documentado todavía no permite cerrar esta fase: no se observó giro en las pruebas de motores, falta validar la calibración con la orientación actual y la última sesión terminó sin enlace.

### Fase 2: waypoints y ajuste de propulsión/control

**Entregables:** misiones cortas, ensayo previo en SITL, pruebas supervisadas en agua protegida, parámetros revisados y un perfil de respuesta del barco.

**Criterios de salida:**

- Repetir las misiones acordadas y medir error de trayectoria, llegada a waypoints, velocidad, rumbo, capacidad de giro y comportamiento de parada.
- Caracterizar respuesta y asimetría de propulsión, zona neutra y límites válidos del conjunto instalado.
- Registrar batería, carga y condiciones del agua para interpretar las diferencias entre ensayos.
- Probar interrupción manual, pérdida de enlace y demás fallos acordados mediante un procedimiento seguro.
- Aprobar un conjunto de parámetros de referencia vinculado a las pruebas que lo justifican.

La expresión «sensores de los motores» se trata como un punto por concretar del inventario. No hay evidencia suficiente para asumir que existen sensores de RPM, encoders o telemetría ESC. Se distinguen calibración del sensor, configuración del ESC y ajuste del control del barco. Se valida cada elemento que realmente esté instalado.

### Fase 3: evasión sencilla con Python

**Entregables:** scripts pequeños para observar, proponer y finalmente ejecutar maniobras limitadas; registros reproducibles; interfaz explícita con ArduPilot.

**Orden de validación:** datos grabados → decisiones sin enviar órdenes → SITL → ensayo real autorizado y supervisado. Se reutilizan las misiones y métricas de la fase 2.

**Criterios de salida:**

- Definir cómo se obtiene información suficiente para evitar un obstáculo: detección, dirección, distancia o zona ocupada, antigüedad e incertidumbre.
- Validar la fuente sensorial elegida con escenas positivas, negativas, objetos pequeños y pérdida de datos.
- Medir latencia de extremo a extremo, margen de separación y éxito en los escenarios acordados.
- Establecer un comportamiento conservador para observación obsoleta, proceso caído, saturación y orden inválida, con posibilidad de intervención humana.
- Ejecutar los escenarios de forma repetible y conservar fallos y límites, además de los aciertos.

Las cajas YOLO actuales proporcionan detecciones en imagen; no acreditan distancia, trayectoria libre o capacidad de evasión. La elección del sensor o método que cubra esa necesidad se documenta antes de habilitar órdenes de movimiento.

### Fase 4: Gazebo e integración ROS 2

**Entregables:** modelo medido del barco, sensores y propulsión simulados, integración con ArduPilot SITL y nodos ROS 2 para percepción, planificación y supervisión.

**Criterios de salida:**

- Entorno fijado y reconstruible con versiones compatibles de sistema operativo, ROS 2, Gazebo, ArduPilot y adaptadores.
- Marcos, unidades, marcas de tiempo y reloj simulado definidos y comprobados.
- Modelo con geometría, masa, empuje, flotación y resistencia suficientes para los ensayos previstos; supuestos y discrepancias respecto al barco real registrados.
- Selección del transporte ROS 2 ↔ ArduPilot mediante una decisión técnica y una prueba mínima con Rover. Se evalúan la interfaz DDS nativa y alternativas MAVLink según las capacidades del firmware que se valide.
- Repetir waypoints, evasión y fallos de las fases anteriores; demostrar que la planificación y la comunicación funcionan bajo degradaciones acordadas.

La documentación de ArduPilot confirma que su plugin de Gazebo puede funcionar sin ROS. Esto permite comprobar primero Gazebo ↔ SITL y añadir después los nodos ROS 2. El modelo marítimo de Kame y su validación siguen siendo trabajo propio del proyecto. Véase [ArduPilot: SITL con Gazebo](https://ardupilot.org/dev/docs/sitl-with-gazebo.html).

La combinación de versiones se decide al comenzar esta fase a partir de la [matriz oficial ROS/Gazebo](https://gazebosim.org/docs/latest/ros_installation/) y de una prueba de integración con ArduPilot. Esta propuesta no fija una distribución sin comprobar el conjunto.

### Fase 5: ROS 2 en el barco y validación en agua

**Entregables:** despliegue reproducible, arranque controlado, supervisión y registros sincronizados de autopiloto, ROS 2, sensores y vídeo.

**Criterios de salida:**

- Repetir comprobaciones de la fase 1 después de instalar la nueva carga de software y verificar recursos, temperatura, alimentación y estabilidad.
- Pasar por observación, decisiones sin órdenes y autoridad de control limitada antes de ampliar el ensayo.
- Repetir primero las misiones sencillas y después los escenarios de evasión aprobados.
- Verificar intervención manual, recuperación y fallos de los procesos, sensores y comunicaciones acordados.
- Comparar métricas reales y simuladas, registrar diferencias y delimitar el entorno en el que se ha demostrado la autonomía.

Las pruebas empiezan en agua protegida y aumentan su alcance con evidencia. El resultado de la fase se expresa como capacidades verificadas bajo condiciones concretas.

## 6. Arquitectura técnica que permite crecer

```text
Fases 1–2
Operador / Cockpit → ArduPilot → control de propulsión
                         ↑
                    sensores del barco

Fase 3
Sensores → observaciones → lógica Python → validación de órdenes → adaptador MAVLink
                                                                        ↓
                                                                    ArduPilot

Fases 4–5
Sensores reales o simulados → nodos ROS 2 → lógica reutilizable → interfaz de vehículo
                                                                        ↓
                                                       ArduPilot real o SITL
```

ArduPilot conserva la responsabilidad de control de bajo nivel y sus mecanismos de seguridad. Python y después ROS 2 solicitan objetivos o consignas a través de una interfaz explícita. Cualquier cambio futuro de esa responsabilidad requiere una decisión y validación propias.

`software/autonomy` mantiene los algoritmos separados del transporte. El adaptador de reproducción permite probarlos con datos grabados. `ros2/kame_navigation` incorpora esos algoritmos mediante una dependencia declarada y añade sus nodos; evita copiar el código Python dentro del workspace.

`interfaces.md` especifica, como mínimo:

- Estado del vehículo con fuente y antigüedad independiente de cada dato.
- Observaciones de obstáculos con unidades, marco, instante e incertidumbre.
- Órdenes permitidas y sus límites: destino, velocidad o la consigna que se acuerde.
- Quién tiene autoridad de mando y cómo se transfiere. Solo un emisor activo de órdenes de autonomía en cada sesión.
- Tratamiento de datos obsoletos, desconexión, órdenes expiradas y pérdida de control.
- Separación de perfiles `replay`, `sitl` y `vehicle`, evitando usar el barco como destino por defecto.

Las medidas físicas y las mallas se mantienen como fuente común en `vehicle/model`. La descripción ROS 2 y el modelo de Gazebo utilizan esos recursos mediante el proceso de construcción. Los parámetros hidrodinámicos propios del simulador se documentan en Gazebo; las copias generadas no se editan manualmente.

Decisiones a registrar cuando se adopten: organización del repositorio, interfaz Python/ArduPilot, estimación de obstáculos, conjunto ROS 2/Gazebo/ArduPilot y transporte ROS 2/vehículo. Cada registro indica contexto, alternativas, decisión, consecuencias y estado: propuesto, aceptado o sustituido.

## 7. Flujo de trabajo para agentes y personas

### Inicio de una tarea

1. Leer el AGENTS raíz, `docs/status.md`, la fase activa y el README del área. Aplicar también el AGENTS de ámbito cuando exista.
2. Usar una tarea con objetivo, alcance, entregables, criterios de aceptación, comprobaciones y relación con la fase. En GitHub la tarea vive en un issue.
3. Identificar qué es modificación local, simulación, despliegue o actuación sobre el vehículo. La aprobación de una PR no constituye por sí sola autorización para actuar sobre el barco.
4. Crear una rama corta y descriptiva para un cambio coherente. Evitar mezclar una migración de carpetas con cambios de navegación o parámetros.

### Ejecución y entrega

1. Preparar el cambio y la documentación mínima que permite usarlo.
2. Ejecutar comprobaciones adecuadas al riesgo y al área. Una corrección documental requiere enlaces y coherencia; un algoritmo necesita casos y escenarios que comprueben su comportamiento.
3. Entregar una PR con el problema resuelto, cambios, comprobaciones y límites de lo verificado. Adjuntar evidencia cuando proceda.
4. Revisar y fusionar conforme a las reglas del repositorio. Las intervenciones sobre el barco se realizan en una sesión autorizada y se registran aparte.
5. Actualizar `docs/status.md` cuando cambie el estado verificado o el bloqueo activo. Actualizar una fase solo con evidencia de sus criterios.

El AGENTS raíz debe caber en una lectura breve: orden de lectura, entorno de destino, prohibición de publicar secretos, límites del vehículo, comprobaciones y entrega. Las instrucciones de comandos y rutas particulares pertenecen a los AGENTS de `vehicle`, `software`, `simulation` y, cuando exista, `ros2`.

Un agente puede completar de forma autónoma cambios locales y ensayos simulados dentro del alcance encargado. Los límites existentes para parámetros, firmware, puertos, reinicios, armado y motores se conservan. La autorización y las condiciones físicas de una sesión se registran con fecha y alcance; no se deducen de un ensayo histórico.

No hace falta mantener una segunda cola de tareas en Markdown. GitHub Issues contiene el trabajo pendiente, los milestones representan fases y los documentos contienen diseño, procedimientos y evidencia. Se incorpora `CODEOWNERS` cuando se conozcan las cuentas responsables.

## 8. Ensayos y trazabilidad

Formato de ID recomendado: `KAME-20261020-001`. No se asigna retrospectivamente a una prueba sin poder reconstruirla.

En Git se guardan `docs/runs/<RUN-ID>/README.md` y `manifest.yaml`, revisados para publicación. Los archivos pesados se guardan en `artifacts/runs/<RUN-ID>/` localmente o en almacenamiento externo documentado. El manifiesto incluye ubicación recuperable y hash para cada archivo; un hash por sí solo no garantiza que la evidencia esté conservada.

Un ensayo registra:

- Objetivo, criterio de fase que comprueba, responsable, fecha/hora y zona horaria.
- Entorno: reproducción, SITL, Gazebo, banco o agua; versión del código y cambios locales si los hubiera.
- Versiones, configuración y parámetros antes/después; calibración y perfil aplicados.
- Condiciones de entrada y, para el barco, autorización y supervisión aplicables.
- Misiones, datos de entrada y comandos o cambios efectivamente realizados.
- Resultado esperado, observado, métricas, fallos y límites.
- Referencias a DataFlash, tlog, vídeo, detecciones, logs de procesos y rosbag cuando existan.
- Estado final y reversión realizada, o pendiente con su motivo.

Para pruebas repetibles se definen antes las tolerancias, duración y número de repeticiones. Esta propuesta no inventa valores de precisión, estabilidad o distancia de seguridad sin conocer el barco y el escenario.

## 9. Preparación para GitHub

### Código y datos

| En Git | Fuera de Git o mediante distribución de artefactos |
| --- | --- |
| Código, README, AGENTS y procedimientos | Entornos virtuales y cachés |
| Configuración de ejemplo sin secretos | Contraseñas, PIN, tokens, claves e identidades ZeroTier |
| Manifiestos con versiones y hashes | Instaladores, binarios compilados y wheels descargados |
| Misiones pequeñas y datos sintéticos | Modelos/pesos descargables y datasets voluminosos |
| Resultados resumidos y fixtures revisados | Vídeos, rosbags, tlogs y DataFlash completos |
| Snapshots de parámetros revisados | Configuración local privada y capturas crudas |

El instalador Cockpit presente supera 100 MiB. GitHub bloquea archivos mayores de 100 MiB en Git normal; su documentación propone Releases para distribuir archivos grandes. Debe conservarse localmente y sustituirse en el repositorio por una referencia verificable. Lo mismo se aplica a wheels, modelos y demás binarios según su procedencia. Fuente: [GitHub: archivos grandes](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

Antes de eliminar una dependencia de la carpeta de trabajo, se comprueba que pueda recuperarse por versión, origen y hash. Los archivos únicos sin fuente reproducible se conservan en un respaldo fuera del repositorio. No se descarta evidencia durante la limpieza.

`assets.yaml` registra plataforma, versión o revisión, URL de origen, SHA-256 y licencia de cada recurso externo. Los hashes pendientes se marcan como pendientes hasta calcularlos. Los lockfiles se generan a partir de entornos validados; no se presentan los nombres de los wheels existentes como prueba de una instalación reproducible.

### Secretos y contenido privado

El AGENTS actual contiene credenciales por una instrucción anterior. La preparación para GitHub requiere trasladarlas a `local/credentials.md` o al almacén privado acordado y hacer que AGENTS indique cómo acceder de forma autorizada. El PIN ya instalado en `/etc/kame/air780eg-pin` mantiene su ubicación operativa; reorganizar el repositorio no requiere cambiarlo en el vehículo.

La revisión previa al primer commit cubre todo el contenido a publicar, incluidos Markdown, respaldos, parámetros, logs, perfiles y fotografías. Se identifican también coordenadas y detalles de red que el propietario prefiera mantener privados. La redacción de copias publicables preserva el original privado y su trazabilidad.

`.gitignore` excluye `local/`, secretos, cachés, estado persistente de SITL, `__pycache__`, entornos virtuales y las carpetas `build/install/log` de ROS 2. Se mantienen los manifiestos y README necesarios mediante excepciones explícitas. Los ignorados se comprueban antes del primer commit.

Se elige licencia para el código propio y se revisan licencias y avisos de los recursos de terceros antes de distribuirlos. La visibilidad pública o privada, el propietario y el nombre del repositorio siguen pendientes de decisión.

### Automatización gradual

- Al inicio: enlaces/documentación, sintaxis y formato de los lenguajes usados, validación de configuraciones y detección de secretos. Se añaden pruebas sobre comportamientos que ya se puedan ejercitar.
- Al disponer de un ensayo SITL repetible: ejecución aislada, escenarios de navegación y publicación de resultados de CI.
- En fase 3: pruebas de decisiones con entradas grabadas y escenarios de fallo.
- En fase 4: construcción con colcon y comprobaciones de los paquetes y escenarios ROS 2/Gazebo.

CI utiliza fixtures, reproducción y simuladores, con destinos locales controlados. No tiene acceso a la red privada del barco ni despliega o calibra el vehículo. Los workflows futuros se habilitan cuando tengan entornos y criterios de resultado definidos.

## 10. Mapa de migración del contenido actual

| Origen actual | Destino propuesto | Tratamiento |
| --- | --- | --- |
| `README.md` | `README.md` y `docs/README.md` | Entrada breve y navegación completa por tareas. |
| `AGENTS.md` | AGENTS raíz y de ámbito | Actualizar fases; conservar límites; trasladar credenciales a almacenamiento privado. |
| `context.md` | Arquitectura, fases, hardware y desarrollo | Distribuir información útil, resolver contradicciones y retirar el resumen duplicado. |
| `docs/estado.md` | `docs/status.md` | Conciliar horas, contraste GPS y evolución de prearm; mantener la última observación fechada. |
| `docs/hardware.md` | `docs/hardware/` y `docs/operations/` | Separar inventario/cableado de calibración y procedimientos. |
| `docs/historial/` | `docs/history/` | Preservar fechas y observaciones; actualizar enlaces e incluir motores en el índice. |
| `yolo-cockpit/` | `software/perception/` | Mover código, configuración, servicios y diagnóstico; separar los recursos descargables. |
| `mobile-access/` | `software/connectivity/` | Mantener script, temporizador, servicio y configuración junto a su guía. |
| `navigator-imu-viewer/` | `software/telemetry-viewer/` | Conservar funcionamiento; mejorar la frescura por mensaje en un cambio posterior. |
| `sitl/start.sh` y parámetros | `simulation/sitl/` | Actualizar rutas y distinguir perfiles simulados de los del vehículo. |
| `sitl/generate_missions.py` | `missions/tools/` | Actualizar el destino de generación. |
| `sitl/misiones/` | `missions/waypoints/cockpit/` | Identificar explícitamente que son borradores de SITL. |
| `sitl/bin/` | `artifacts/cache/` y manifiestos | Conservar localmente; verificar procedencia antes de retirar de la distribución. |
| `sitl/state/` | Estado ignorado bajo `artifacts/` | Documentar persistencia y efecto de `--wipe`. |
| `backups/*.params` y compases | `vehicle/parameters/snapshots/` o evidencia privada | Revisar contenido y vincular a la sesión. No convertir automáticamente en baseline. |
| `backups/*.BIN` | `artifacts/runs/` o archivo externo | Conservar el original e indexarlo cuando se identifique su sesión. |
| Log y capturas de la raíz | Evidencia fechada e indexada | Mantener originales; publicar únicamente copias revisadas que aporten evidencia. |
| Wheels y pesos YOLO | Caché local y manifiestos | Documentar instalación y recuperación. |
| `__pycache__/` | Archivos ignorados | Excluir de la publicación. |

Mover un archivo local no modifica sus rutas en la Raspberry. Las rutas de instalación `/opt/...`, `/home/pi/...` y systemd siguen siendo un contrato de despliegue hasta que se prepare y autorice un cambio específico.

## 11. Orden de implementación de la reestructuración

1. **Preservar e inventariar:** respaldo local completo, lista de archivos y tamaños, identificación de contenido único, secretos y artefactos.
2. **Acordar y redactar las fuentes de documentación:** fase actual, roadmap, arquitectura, inventario, procedimientos y reglas de agentes. Resolver las discrepancias detectadas sin inventar nuevas observaciones.
3. **Mover los componentes existentes:** actualizar enlaces, imports, rutas relativas de scripts y documentación de despliegue. Mantener las rutas operativas del vehículo.
4. **Separar recursos y configuración privada:** conservarlos fuera del contenido a publicar y crear sus manifiestos recuperables.
5. **Verificar la migración:** comprobar enlaces, generación de misiones en destino temporal, arranque local con fixtures cuando corresponda y funcionamiento de rutas de SITL en el entorno compatible. Registrar lo que no se pudo ejecutar.
6. **Preparar Git y GitHub:** crear ignore/atributos, revisar el contenido exacto del primer commit, incorporar plantillas y CI inicial, elegir licencia, propietario y visibilidad, y publicar dentro del alcance autorizado.
7. **Retomar la fase 1:** convertir sus bloqueos actuales en tareas concretas y reunir evidencia para sus criterios de salida.

El resultado de esta primera migración será un repositorio navegable, con los componentes actuales en su ubicación definitiva y las cinco fases documentadas. Los algoritmos de evasión, el modelo Gazebo y los paquetes ROS 2 se implementarán al llegar a sus fases.

## 12. Decisiones que quedan abiertas

| Decisión | Momento necesario |
| --- | --- |
| Cuenta, nombre, visibilidad y licencia de GitHub | Antes de publicar. |
| Archivo privado de evidencias y recursos no reproducibles | Antes de retirar esos archivos de la distribución. |
| Identidad exacta de ESC, motores y sensores de propulsión por lado | Fase 1. |
| Tolerancias, duración y repeticiones de cada criterio de validación | Antes de ejecutar cada campaña de ensayos. |
| Método sensorial para estimar obstáculos y espacio libre | Inicio de fase 3. |
| Máquina de simulación y conjunto OS/ROS 2/Gazebo/ArduPilot | Inicio de fase 4. |
| Transporte ROS 2/ArduPilot y recursos de cómputo a bordo | Validación en fase 4 antes de la transferencia al barco. |

Estas decisiones no impiden preparar la documentación y la migración local de los componentes existentes.
