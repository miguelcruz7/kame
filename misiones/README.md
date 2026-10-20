# Misiones de Kame

`cockpit/` contiene dos **borradores para SITL**, alrededor de `43.340080,-8.384526`, con crucero de 1,2 m/s: ida y vuelta y triángulo. No son misiones aprobadas para el barco real.

Desde la raíz, con Python 3.12+:

```sh
python misiones/generate_missions.py
python misiones/generate_missions.py --output-dir /ruta/temporal
```

Sin argumento se sobrescriben los dos `.cmp` de `misiones/cockpit/`, independientemente del directorio de trabajo. Con `--output-dir` solo se escribe en ese destino. Los identificadores son deterministas y el contenido conserva las misiones anteriores.

El [SITL](../simulacion/sitl/README.md) no abre ni configura Cockpit. Configurar su conexión local e importar los `.cmp` por separado. Antes de usar una misión con el barco, revisar origen, límites y escenario, ensayarla en simulación y cumplir la fase activa del [plan](../docs/plan.md).
