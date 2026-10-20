#!/usr/bin/env bash
set -euo pipefail

sitl_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ardupilot_dir="${ARDUPILOT_DIR:-$HOME/ardupilot}"
bridge="${sitl_dir}/bin/mavlink2rest"
rover="${sitl_dir}/bin/ardurover"

if [[ ! -x "$bridge" || ! -x "$rover" ]]; then
  echo "Faltan los binarios de SITL o mavlink2rest en ${sitl_dir}/bin" >&2
  exit 1
fi

"$bridge" -c udpin:127.0.0.1:14550 -s 127.0.0.1:8088 &
bridge_pid=$!
trap 'kill "$bridge_pid" 2>/dev/null || true' EXIT

defaults="${ardupilot_dir}/Tools/autotest/default_params/rover.parm,${ardupilot_dir}/Tools/autotest/default_params/motorboat.parm,${ardupilot_dir}/Tools/autotest/default_params/rover-skid.parm,${sitl_dir}/virtual-params.parm"

cd "${sitl_dir}/state"
"$rover" \
  --wipe \
  --model motorboat-skid \
  --speedup 1 \
  --serial0=udpclient:127.0.0.1:14550 \
  --defaults "$defaults" \
  --home 43.340080,-8.384526,0,270
