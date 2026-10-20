# Normas de trabajo en Kame

## Orden de lectura

Leer el [estado y siguiente trabajo](docs/estado.md), el [plan](docs/plan.md) y el README del componente afectado. Para intervenir en el vehículo, consultar también [hardware](docs/hardware.md) y [preparación](docs/preparacion.md).

Este documento contiene reglas estables. Los avances, fases activas, lecturas e incidencias pertenecen a sus documentos de referencia.

## Flujo de trabajo

Seguir: tarea con objetivo y criterios de aceptación → rama → cambio → comprobaciones → revisión → resultado registrado. Consultar el siguiente trabajo en el estado; usar los issues enlazados cuando estén disponibles.

- Mantener código, configuración y README juntos. Evitar duplicar información y crear carpetas para funcionalidades aún no implementadas.
- Separar cambios de organización y cambios funcionales. Un traslado local no modifica las rutas instaladas en el vehículo.
- Antes de entregar, ejecutar desde la raíz `python .github/checks/check_repository.py`, con Python 3.12+, Node.js 20+ y Git. No necesita acceso al barco.
- Para cambios de navegación o del arranque SITL, ejecutar además `python3 .github/checks/check_sitl.py` en Linux/WSL con los recursos de su [guía](simulacion/sitl/README.md).
- Registrar comprobaciones, resultados y límites. No atribuir a una prueba de software resultados físicos que no se observaron.

## Límites de actuación

Empezar las inspecciones con consultas de solo lectura y seguir los procedimientos del subsistema. Verificar que la interfaz utilizada corresponde a la versión instalada y que cada lectura es fresca.

No cambiar parámetros, firmware o asignaciones de puerto, ni reiniciar, armar o accionar motores sin autorización explícita y comprobación de seguridad. Mantener el barco desarmado mientras existan avisos de brújula o no se haya validado el GPS. Una autorización histórica no acredita las condiciones físicas de una nueva sesión.

Antes de un cambio autorizado, guardar la configuración vigente; aplicar solo lo acordado, leer el resultado y registrar valores anterior/nuevo, fecha, comprobaciones y reversión. Consultar las guías de [vídeo](software/video/README.md) y [conectividad](software/conectividad/README.md) antes de intervenir en esos servicios.

## Credenciales y recursos privados

Las credenciales operativas se conservan en `local/credenciales.md`, excluido de Git. Leerlas solo cuando una tarea autorizada las necesite y mantenerlas ahí si cambian. No copiarlas a archivos versionados, salida de comandos, issues o PR. Proteger también tokens, claves e identidades de red.

Mantener binarios, modelos, cachés y registros pesados en `local/`. Su procedencia y recuperación están en el [inventario](docs/historial/recursos.json); preservar los archivos únicos durante una limpieza.

## Documentación y registro

- README: orientación, estructura y comandos de entrada.
- Plan: objetivos y criterios para avanzar.
- Estado: fase activa, hechos, pendientes y siguiente trabajo.
- Preparación y guías de componentes: procedimientos repetibles.
- Hardware: inventario, montaje y conexiones.
- Historial: observaciones, decisiones y ensayos fechados.

Actualizar solo los documentos afectados por una tarea. Distinguir lecturas directas, comunicaciones del usuario e hipótesis; registrar fecha, fuente, enlace cuando exista y límites. Conservar los hechos históricos con su fecha.

Un ensayo registra ID, objetivo, entorno, versión Git y cambios locales, configuración antes/después, autorización aplicable, resultado, evidencias recuperables y estado final/reversión. Los detalles van en el [historial](docs/historial/README.md); los datos crudos privados se conservan bajo un ID común fuera de Git.
