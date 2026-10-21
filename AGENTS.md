# Normas de trabajo en Kame

## Alcance y orden de lectura
1. Leer este documento y abrir el [README principal](README.md) ([Por dónde empezar](README.md#por-dónde-empezar)) sin releer lo ya visto.
2. Ceñirse al encargo actual y leer las guías que requiera. Consultar `docs/estado.md` o `docs/plan.md` aporta contexto, pero **no autoriza a ejecutar otros pendientes**.
3. Si surge un problema fuera de alcance, registrarlo como pendiente sin resolverlo (salvo que bloquee el encargo actual). Al terminar el encargo, detenerse.

## Actuación según el encargo

| Encargo | Qué hacer | Entrega esperada |
| --- | --- | --- |
| **Pregunta o análisis** | Consultar documentación y código pertinentes. No editar archivos, no crear ramas ni correr pruebas. | Explicación o informe con hechos y límites. |
| **Cambio documental** | Editar documentos afectados; verificar coherencia, enlaces y referencias. | Cambios y comprobaciones registrados. |
| **Cambio de código** | Leer guía del componente, implementar, verificar y actualizar su guía si cambia el uso. | Cambios, comprobaciones y límites registrados. |
| **Inspección del vehículo** | Leer `hardware.md`, `preparacion.md` y guía del subsistema; hacer lecturas frescas de solo lectura. | Síntesis en `estado.md` y evidencia en `historial/`. |
| **Intervención en el vehículo** | Confirmar autorización y seguridad, guardar backup, aplicar cambio y verificar. | Valores anterior/nuevo, evidencia, estado final y reversión. |

## Flujo de trabajo y Git
1. **Preparación:** Definir objetivo, alcance y criterios de aceptación (enlazar issue/PR si existe). Comprobar rama y cambios locales antes de editar para conservar trabajo ajeno.
2. **Estructura:** Mantener código, configuración y README juntos; no crear carpetas vacías ni duplicar. Separar refactorización organizativa de cambios funcionales (mover archivos locales no altera las rutas instaladas en el barco).
3. **Control de versiones:** Puedes crear ramas o commits locales para aislar trabajo. **Prohibido hacer `push`, abrir PR o integrar en `main` sin autorización explícita.** Una PR integrada no equivale a código instalado en el barco.
4. **Cierre:** Revisar `git diff` (alcance, efectos, docs, secretos). Entregar qué cambió, qué se comprobó, qué queda pendiente y distinguir entre *en repositorio*, *instalado* y *verificado en ejecución*. Tras integrar (con permiso), sincronizar `main` local sin borrar trabajo ajeno.

## Comprobaciones y bloqueo
- **Archivos versionados:** Ejecutar en raíz `python3 .github/checks/check_repository.py` (Python 3.12+, Node 20+, Git; no requiere el barco).
- **Navegación o SITL:** Ejecutar además `python3 .github/checks/check_sitl.py` en Linux/WSL según su [guía](simulacion/sitl/README.md).
- **Específicas:** Añadir pruebas si las anteriores no cubren los criterios de aceptación. Las pruebas simuladas no acreditan resultados físicos.
- **Traspaso de trabajo incompleto:** Si un bloqueo externo impide verificar, no cerrar la tarea. Documentar estado actual, métodos probados, cambios aplicados/revertidos, hipótesis abiertas (nunca presentarlas como hechos), evidencias y siguiente paso. Registrar intervenciones/ensayos en `docs/historial/` (y actualizar `docs/estado.md` si cambia el estado vigente); cambios puramente de software van en su PR/issue.

## Límites de actuación en el vehículo
- **Interfaz:** Usar siempre la interfaz de mayor nivel verificable: BlueOS, ArduPilot o MAVLink para configuración/estado; SSH para SO, servicios, archivos y red. No usar bajo nivel para algo gestionado arriba sin razón técnica. Verificar que la interfaz corresponde a la versión instalada.
- **Seguridad física:** Prohibido cambiar parámetros, firmware o puertos, ni reiniciar, armar o mover motores sin **autorización explícita de la sesión actual** (permisos pasados caducan) y comprobación de seguridad. **Mantener desarmado si hay avisos de brújula o sin GPS válido.**
- **Ejecución:** Consultar guías de [vídeo](software/video/README.md) y [conectividad](software/conectividad/README.md) antes de tocar esos servicios. Guardar siempre configuración previa y registrar fecha, valores anterior/nuevo, pruebas y plan de reversión.

## Credenciales y archivos locales
- Leer credenciales de `local/credenciales.md` (excluido de Git) solo cuando una tarea autorizada lo requiera. Si el usuario autoriza expresamente una conexión que las necesita, esa autorización permite leerlas y usarlas sin volver a pedirlas; no incluirlas en comandos, respuestas ni registros. Jamás exponer claves, tokens o identidades de red en Git, logs, issues o PRs.
- Antes de intentar SSH a Kame, consultar el método de autenticación indicado en `local/credenciales.md`. El acceso actual del usuario `pi` usa contraseña; las claves privadas que OpenSSH encuentre en el PC no son credenciales del barco. Para `kame-4g`, usar autenticación por contraseña y evitar `BatchMode=yes`, que impide solicitarla.
- Guardar binarios, modelos, cachés y logs pesados en `local/`. Consultar el [inventario](docs/historial/recursos.json) para su procedencia y preservar archivos únicos al limpiar.

## Qué documentación actualizar
Actualizar solo los archivos afectados distinguiendo lecturas directas, dichos del usuario e hipótesis (con fecha, fuente y enlaces):
- **Estructura o comandos de entrada:** [README](README.md)
- **Objetivos o fases:** [Plan](docs/plan.md)
- **Evidencia vigente, bloqueos o siguientes pasos:** [Estado](docs/estado.md)
- **Inventario, cableado o montaje:** [Hardware](docs/hardware.md)
- **Procedimiento de preparación/ensayo:** [Preparación](docs/preparacion.md)
- **Uso o instalación de un módulo:** `README.md` del componente
- **Ensayos, incidencias o cambios operativos del barco:** Entrada fechada en [historial](docs/historial/README.md) (incluir ID, objetivo, fecha/zona, fuente, entorno, commit/cambios locales, config antes/después, autorización, resultado, evidencias y reversión; datos crudos en `local/` bajo el mismo ID).
