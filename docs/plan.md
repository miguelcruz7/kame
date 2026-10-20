# Plan de Kame

La fase activa es la **1: preparación y validación del barco**. Las fases se cierran con evidencia, no por tener archivos o servicios instalados. El [estado](estado.md) conserva los bloqueos y el siguiente trabajo; la [preparación](preparacion.md) explica el procedimiento actual.

| Fase | Objetivo | Entregables y criterios de salida |
| --- | --- | --- |
| 1. Preparación | Configurar BlueOS, firmware, sensores y propulsión. | Inventario y cableado confirmados; versiones y respaldo recuperables; sensores calibrados; GPS/posición, actitud y rumbo validados; ESC/motores comprobados; control manual, parada, enlace y recuperación verificados con supervisión. |
| 2. Waypoints | Repetir misiones básicas y ajustar el comportamiento del barco. | Ensayos en SITL y después en agua protegida; error de trayectoria, velocidad, giros y parada medidos; respuesta por motor caracterizada; parámetros de referencia aprobados con evidencia. |
| 3. Evasión Python | Incorporar detección de obstáculos y maniobras sencillas. | Fuente sensorial suficiente para estimar obstáculos y espacio libre; lógica probada con grabaciones, sin órdenes, en SITL y después bajo supervisión; latencia, separación, falsas alarmas y fallos evaluados. |
| 4. Gazebo y ROS 2 | Modelar el barco e integrar autonomía avanzada en simulación. | Modelo físico documentado; versiones compatibles fijadas; integración con ArduPilot SITL; marcos, unidades y reloj comprobados; misiones y fallos repetibles mediante ROS 2. |
| 5. ROS 2 en agua | Transferir y validar la autonomía en el barco real. | Despliegue y recuperación reproducibles; recursos de cómputo y estabilidad comprobados; intervención manual; waypoints y evasión evaluados progresivamente y comparados con simulación. |

## Cómo avanzar

Antes de cada campaña se acuerdan métricas, tolerancias, duración y repeticiones según el escenario y el barco. Registrar cada criterio como pendiente, en curso, verificado, fallido o no aplicable con justificación y evidencia. Un criterio fallido sigue abierto.

SITL permite ensayar cambios desde las fases iniciales. Los cambios de navegación se ensayan primero allí. Gazebo y ROS 2 se implementan durante la fase 4; sus paquetes se crean cuando exista trabajo concreto.

En la fase 1, 4G es requisito si la siguiente campaña depende de ese enlace. El vídeo debe verificarse en Cockpit cuando forme parte de la supervisión. Los incidentes de armado inesperado y pérdida de telemetría necesitan una disposición documentada antes de ampliar los ensayos.

## Decisiones que condicionan las fases siguientes

- **Propulsión:** identificar ESC y motor por lado. «Sensores de los motores» no presupone encoders, RPM ni telemetría ESC instalados. Separar calibración de sensores, configuración del ESC y ajuste del control.
- **Percepción:** las cajas YOLO actuales no demuestran distancia ni espacio libre. Elegir y validar el método sensorial antes de habilitar evasión activa. YOLO sigue siendo apoyo visual experimental.
- **Arquitectura:** ArduPilot conserva el control de bajo nivel; Python y después ROS 2 solicitan objetivos o consignas mediante un adaptador explícito. Mantener lógica reutilizable y una sola autoridad de mando de autonomía.
- **Gazebo/ROS 2:** elegir al comenzar la fase 4 el conjunto OS/ROS 2/Gazebo/ArduPilot y el transporte compatible con Rover. Documentar ejes del casco, transformaciones, unidades, marcas de tiempo y antigüedad de datos. No presentar versiones futuras como verificadas.
- **Modelo:** medir geometría, masa y respuesta del barco; documentar supuestos de empuje, flotación y resistencia. La simulación no demuestra por sí sola comportamiento en agua.

## Organización del código

Los componentes de `software/` conservan sus servicios, configuración y README. `misiones/` contiene borradores y generador; `simulacion/sitl/` contiene el simulador. En fase 3 se añadirá `software/autonomia/`; en fase 4 se añadirán Gazebo y el workspace ROS 2. Las reglas están en [AGENTS.md](../AGENTS.md).

Las propuestas extensas y el antiguo contexto se consolidaron aquí, en preparación, hardware y los README. Sus originales permanecen en el respaldo y el commit inicial saneado, sin mantener un segundo estado activo.
