"""Ensayo Linux de SITL y limpieza de sus procesos; solo loopback, sin órdenes."""

import json
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import ProxyHandler, build_opener


ROOT = Path(__file__).resolve().parents[2]
OPENER = build_opener(ProxyHandler({}))


def port_free(port, kind):
    with socket.socket(socket.AF_INET, kind) as sock:
        if kind == socket.SOCK_STREAM:
            # Permitir TIME_WAIT de una prueba anterior, sin compartir un listener.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def group_members(group):
    members = []
    for path in Path("/proc").glob("[0-9]*/stat"):
        try:
            # Después del último ')' vienen estado, ppid y pgrp.
            fields = path.read_text().rsplit(")", 1)[1].split()
            if int(fields[2]) == group and fields[0] != "Z":
                members.append(int(path.parent.name))
        except (OSError, ValueError, IndexError):
            continue
    return members


def heartbeat():
    url = "http://127.0.0.1:8088/v1/mavlink/vehicles/1/components/1/messages/HEARTBEAT"
    with OPENER.open(url, timeout=1) as response:
        entry = json.load(response)
    return entry


def mode_bits(message):
    value = message["base_mode"]
    value = value["bits"] if isinstance(value, dict) else value
    try:
        return int(value)
    except (ValueError, TypeError):
        # Este binario MAVLink2REST serializa bitflags como nombres unidos por '|'.
        flags = {
            "MAV_MODE_FLAG_CUSTOM_MODE_ENABLED": 1,
            "MAV_MODE_FLAG_TEST_ENABLED": 2,
            "MAV_MODE_FLAG_AUTO_ENABLED": 4,
            "MAV_MODE_FLAG_GUIDED_ENABLED": 8,
            "MAV_MODE_FLAG_STABILIZE_ENABLED": 16,
            "MAV_MODE_FLAG_HIL_ENABLED": 32,
            "MAV_MODE_FLAG_MANUAL_INPUT_ENABLED": 64,
            "MAV_MODE_FLAG_SAFETY_ARMED": 128,
        }
        bits = 0
        for name in str(value).split("|"):
            bits |= flags[name.strip()]
        return bits


def main():
    if sys.platform != "linux":
        raise SystemExit("Ejecutar esta comprobación en Linux/WSL; no consulta el barco")
    assert port_free(8088, socket.SOCK_STREAM), "HTTP 8088 ocupado; no se detiene el proceso existente"
    assert port_free(14550, socket.SOCK_DGRAM), "UDP 14550 ocupado; no se detiene el proceso existente"
    script = ROOT / "simulacion/sitl/start.sh"
    subprocess.run(["bash", "-n", str(script)], check=True)
    for name in ("ardurover", "mavlink2rest"):
        assert os.access(ROOT / "local/bin/sitl" / name, os.X_OK), f"Falta ejecutable local: {name}"

    logs = ROOT / "local/registros/sitl"
    logs.mkdir(parents=True, exist_ok=True)
    log_path = logs / ("check-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%fZ") + ".log")
    print("Iniciando ensayo SITL local (máximo 40 s de arranque)", flush=True)
    counter_first = None
    counter_last = None
    problem = None
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(["bash", str(script)], cwd=ROOT, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 40
            last_problem = "Sin heartbeat"
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f"SITL terminó con código {process.returncode}")
                try:
                    entry = heartbeat()
                    counter = int(entry["status"]["time"]["counter"])
                    assert not mode_bits(entry["message"]) & 128, "El SITL está armado"
                    if counter_first is None:
                        counter_first = counter
                    elif counter > counter_first:
                        counter_last = counter
                        break
                except (OSError, ValueError, KeyError) as error:
                    last_problem = str(error)
                time.sleep(0.5)
            assert counter_last is not None, f"No hubo dos heartbeat frescos: {last_problem}"
        except BaseException as error:
            problem = error
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                problem = problem or RuntimeError("El lanzador no respondió a SIGTERM")
            deadline = time.monotonic() + 3
            while group_members(process.pid) and time.monotonic() < deadline:
                time.sleep(0.1)
            leaked = group_members(process.pid)
            if leaked:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
                problem = problem or RuntimeError(f"Procesos SITL no limpiados por el lanzador: {leaked}")
            if not port_free(8088, socket.SOCK_STREAM) or not port_free(14550, socket.SOCK_DGRAM):
                problem = problem or RuntimeError("Los puertos de SITL no quedaron libres")
    if problem:
        print(log_path.read_text(encoding="utf-8", errors="replace")[-6000:], file=sys.stderr)
        raise problem
    print(f"OK: heartbeat {counter_first} → {counter_last}, desarmado; procesos y puertos liberados")
    print(f"Registro: {log_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
