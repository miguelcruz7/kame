#!/usr/bin/env bash
set -euo pipefail

sitl_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd -- "${sitl_dir}/../.." && pwd)"
ardupilot_dir="${ARDUPILOT_DIR:-$HOME/ardupilot}"
bridge="${project_dir}/local/bin/sitl/mavlink2rest"
rover="${project_dir}/local/bin/sitl/ardurover"
state_dir="${project_dir}/local/estado/sitl"

if [[ ! -x "$bridge" || ! -x "$rover" ]]; then
  echo "Faltan ejecutables en ${project_dir}/local/bin/sitl; consultar el README de SITL" >&2
  exit 1
fi

defaults="${ardupilot_dir}/Tools/autotest/default_params/rover.parm,${ardupilot_dir}/Tools/autotest/default_params/motorboat.parm,${ardupilot_dir}/Tools/autotest/default_params/rover-skid.parm,${sitl_dir}/virtual-params.parm"
for filename in rover.parm motorboat.parm rover-skid.parm; do
  if [[ ! -r "${ardupilot_dir}/Tools/autotest/default_params/${filename}" ]]; then
    echo "No se encuentra ${filename}; comprobar ARDUPILOT_DIR" >&2
    exit 1
  fi
done

bridge_pid=""
rover_pid=""
cleanup() {
  trap - EXIT INT TERM
  [[ -z "$rover_pid" ]] || kill "$rover_pid" 2>/dev/null || true
  [[ -z "$bridge_pid" ]] || kill "$bridge_pid" 2>/dev/null || true
  [[ -z "$rover_pid" ]] || wait "$rover_pid" 2>/dev/null || true
  [[ -z "$bridge_pid" ]] || wait "$bridge_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

mkdir -p "$state_dir"
"$bridge" -c udpin:127.0.0.1:14550 -s 127.0.0.1:8088 &
bridge_pid=$!

cd "$state_dir"
"$rover" \
  --wipe \
  --model motorboat-skid \
  --speedup 1 \
  --serial0=udpclient:127.0.0.1:14550 \
  --defaults "$defaults" \
  --home 43.340080,-8.384526,0,270 &
rover_pid=$!
wait "$rover_pid"
rover_pid=""
