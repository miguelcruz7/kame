# Publicación en GitHub — 2026-10-20

El usuario autorizó subir Kame a GitHub para facilitar su análisis desde ChatGPT. Se publica como repositorio público [miguelcruz7/kame](https://github.com/miguelcruz7/kame), con rama principal `main`. Esta tarea afecta al repositorio y su documentación; no incluye inspección ni cambios en el vehículo.

## Contenido y preservación

- Se incluyen código, configuración revisada, documentación, misiones de SITL y comprobaciones. `local/` permanece excluido: credenciales, identificadores de red, ejecutables, modelos, wheels, capturas y registros crudos no se publican.
- Antes de publicar se verificó una copia completa del historial local: `local/registros/publicacion/20261020-130734/historial-privado-antes-publicacion.bundle`. El registro de esa carpeta conserva las referencias anteriores y nuevas, y una exportación del historial original.
- Se revisaron los 85 blobs de los seis commits existentes antes de esta tarea: sin archivos de `local/`, recursos pesados ni coincidencias con las dos credenciales operativas conocidas o los patrones de secretos comprobados. Los identificadores de la red ZeroTier y sus dos nodos sí figuraban en documentos y versiones anteriores.
- Se retiraron esos tres identificadores de todas las ramas locales antes de publicarlas. Esto cambió los hashes de los seis commits; se conservan sus mensajes, autoría, fechas y estructura. Los valores originales quedan en `local/red.md`, con el historial anterior en el respaldo privado. El nuevo historial importado pasó `git fsck --full` y la revisión de contenido.
- Se mantienen IP privadas de las guías y coordenadas de los borradores de simulación; no se han convertido en una nueva lectura de posición del barco.
- No se añade una licencia propia en esta tarea. Su elección y la revisión de licencias de dependencias permanecen pendientes; no se distribuyen modelos ni paquetes de terceros.

## Flujo de trabajo

Tarea con criterios de aceptación → rama → cambios → comprobaciones locales → pull request → revisión y comprobaciones de GitHub Actions → integración en `main` → resultado registrado. Las plantillas existentes están disponibles para tareas y PR.

La publicación inicial integra la rama local `chore/publicar-github` tras revisar sus diferencias y ejecutar las comprobaciones. Las tareas y criterios físicos de fase 1 permanecen en [estado.md](../estado.md).

## Verificación

Ejecutar `python -X utf8 .github/checks/check_repository.py` desde la raíz. Comprueba sintaxis, configuración, enlaces, patrones de secretos, equivalencia de misiones y visor con telemetría simulada. No requiere acceso al barco ni a recursos privados.

Antes del envío pasaron las comprobaciones portátiles en Windows: 55 archivos, 137 enlaces/anclas, sintaxis/configuración, patrones de secretos, misiones equivalentes y página/API/SSE del visor simulado. También pasó `git diff --check`.

El workflow de [GitHub Actions](https://github.com/miguelcruz7/kame/actions/workflows/checks.yml) ejecuta estas comprobaciones en Ubuntu al enviar cambios o abrir una PR. La [primera ejecución](https://github.com/miguelcruz7/kame/actions/runs/39412961075), sobre `63b88fe`, terminó correctamente en Ubuntu 24.04.

También se verificó sin autenticación que el repositorio es público, que `main` es la rama predeterminada y que README, AGENTS, plan y estado responden HTTP 200 con el contenido publicado. Un clon público nuevo, sin credenciales ni carpeta `local/`, pasó las comprobaciones portátiles completas.

La revisión final de los siete commits enviados inicialmente cubrió 93 blobs: sin archivos privados ni pesados, sin coincidencias con las dos credenciales conocidas y sin los tres identificadores privados de red. La copia de trabajo quedó sincronizada con `origin/main`. Estos resultados no sustituyen los ensayos pendientes del vehículo.
