# Normas de trabajo en Kame

## Orden de lectura

Este documento contiene reglas estables. Tras leerlas, abrir el [README principal](README.md) para conocer el proyecto y seguir su recorrido de [Por dónde empezar](README.md#por-dónde-empezar), sin repetir lecturas ya completadas.

Trabajar sobre el encargo del usuario. El estado y el plan aportan contexto; consultar sus pendientes no autoriza a ejecutarlos todos. Leer las guías y antecedentes que requiera la tarea.

## Actuación según el encargo

| Encargo | Qué hacer | Entrega esperada |
| --- | --- | --- |
| Pregunta o análisis | Consultar la documentación y el código pertinentes; responder con hechos y límites. | Explicación o informe. La consulta por sí sola no requiere editar archivos, crear rama ni ejecutar pruebas. |
| Cambio documental | Editar los documentos afectados y comprobar coherencia, enlaces y referencias. | PR con el cambio y sus comprobaciones. |
| Cambio de código | Leer la guía del componente, implementar y verificar el comportamiento; actualizar su guía si cambia el uso. | PR con resultado, comprobaciones y límites. |
| Inspección del vehículo | Leer hardware, preparación y guía del subsistema; obtener lecturas actuales de solo lectura. | Síntesis en estado y evidencia detallada en historial cuando corresponda. |
| Intervención en el vehículo | Confirmar autorización y seguridad, guardar configuración, aplicar lo autorizado y verificar el resultado. | Registro de valores anterior/nuevo, evidencia, estado final y reversión. |

Si una inspección o intervención genera cambios en archivos versionados, aplicar también el flujo de Git.

## Flujo de trabajo

Para cambios versionados: tarea → rama → cambio → comprobaciones → revisión → PR → integración cuando proceda → resultado registrado.

1. Definir objetivo, alcance y criterios de aceptación en el encargo, issue o PR; enlazar la tarea existente cuando la haya.
2. Comprobar rama y cambios locales antes de editar. Crear una rama adecuada a la tarea y conservar el trabajo ajeno.
3. Mantener código, configuración y README juntos; evitar duplicaciones y carpetas para funciones aún no implementadas. Separar cambios de organización y funcionales; un traslado local no cambia las rutas instaladas en el vehículo.
4. Ejecutar las comprobaciones siguientes y revisar las diferencias antes de crear el commit, subir la rama y abrir la PR.
5. Entregar rama/PR o commit, resultado, comprobaciones y pendientes. Distinguir lo preparado en el repositorio, lo instalado y lo verificado en ejecución. Tras integrar, sincronizar `main` local sin descartar trabajo ajeno.

## Comprobaciones y cierre

- Para cambios en archivos versionados, ejecutar desde la raíz `python .github/checks/check_repository.py`, con Python 3.12+, Node.js 20+ y Git. No necesita acceso al barco.
- Para cambios en código de navegación o en el arranque de SITL, ejecutar además `python3 .github/checks/check_sitl.py` en Linux/WSL con los recursos de su [guía](simulacion/sitl/README.md).
- Añadir comprobaciones del comportamiento modificado cuando las anteriores no cubran sus criterios de aceptación.
- Registrar comando o ensayo, entorno, resultado y límites. Si falta una dependencia, recurso o acceso, indicar qué comprobación queda pendiente y cómo desbloquearla; continuar el trabajo independiente posible.

Cerrar una tarea solo cuando se cumplan sus criterios y comprobaciones exigidas. Corregir los fallos y repetir las pruebas afectadas. Si un impedimento externo bloquea la verificación, entregar el trabajo como incompleto indicando qué falta; una prueba no ejecutada permanece pendiente. Las pruebas simuladas no acreditan resultados físicos.

## Revisión e integración

El agente revisa sus diferencias: alcance, efectos, documentación, secretos y resultados. Si el encargo reserva la revisión a una persona u otro revisor, mantener la PR pendiente hasta recibirla.

Para documentación y software local dentro del encargo autorizado, el agente puede integrar su PR cuando las comprobaciones exigidas del último commit pasan, se han resuelto los hallazgos y no hay revisión pendiente. Si falta una condición, entregar la PR indicando cuál. Una PR integrada no acredita instalación ni autorización para actuar sobre el vehículo; se aplican los límites siguientes.

## Límites de actuación

Empezar las inspecciones con consultas de solo lectura y seguir los procedimientos del subsistema. Verificar que la interfaz utilizada corresponde a la versión instalada y que cada lectura es fresca.

No cambiar parámetros, firmware o asignaciones de puerto, ni reiniciar, armar o accionar motores sin autorización explícita y comprobación de seguridad. Mantener el barco desarmado mientras existan avisos de brújula o no se haya validado el GPS. Una autorización histórica no acredita las condiciones físicas de una nueva sesión.

Antes de un cambio autorizado, guardar la configuración vigente; aplicar solo lo acordado, leer el resultado y registrar valores anterior/nuevo, fecha, comprobaciones y reversión. Consultar las guías de [vídeo](software/video/README.md) y [conectividad](software/conectividad/README.md) antes de intervenir en esos servicios.

## Credenciales y recursos privados

Las credenciales operativas se conservan en `local/credenciales.md`, excluido de Git. Leerlas solo cuando una tarea autorizada las necesite y mantenerlas ahí si cambian. No copiarlas a archivos versionados, salida de comandos, issues o PR. Proteger también tokens, claves e identidades de red.

Mantener binarios, modelos, cachés y registros pesados en `local/`. Su procedencia y recuperación están en el [inventario](docs/historial/recursos.json); preservar los archivos únicos durante una limpieza.

## Qué documentación actualizar

| Qué cambia | Dónde registrarlo |
| --- | --- |
| Estructura, componentes o comandos de entrada | [README](README.md). |
| Objetivos, fases o criterios de avance acordados | [Plan](docs/plan.md). |
| Evidencia vigente, bloqueos, prioridades o siguientes tareas | [Estado](docs/estado.md), con fecha y fuente. |
| Inventario, cableado, montaje u orientación | [Hardware](docs/hardware.md). |
| Procedimiento de preparación o ensayo del barco | [Preparación](docs/preparacion.md). |
| Instalación, operación, verificación o recuperación de un componente | README del componente. |
| Reglas estables de trabajo | AGENTS. |
| Resultados detallados, incidencias, decisiones o cambios operativos | Entrada fechada en [historial](docs/historial/README.md). |

Actualizar solo los documentos afectados. Un cambio editorial no constituye una nueva inspección del barco. Distinguir lecturas directas, comunicaciones del usuario e hipótesis; registrar fecha, fuente, enlace cuando exista y límites. Conservar las observaciones históricas con su fecha.

Un ensayo registra ID, objetivo, fecha/zona horaria, fuente y enlace usado, entorno, versión Git y cambios locales, configuración antes/después, autorización aplicable, resultado, evidencias recuperables y estado final/reversión. Los detalles van al historial; los datos crudos privados se conservan bajo un ID común fuera de Git. Los cambios ordinarios de documentación o software pueden quedar registrados en su PR sin añadir una entrada al historial del vehículo.
