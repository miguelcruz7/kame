"""Captura de solo lectura para el ensayo estático de Kame.

Los datos quedan en local/. Ningun subcomando cambia la configuracion del barco.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import math
import pathlib
import re
import shlex
import subprocess
import sys
import threading
import time
import urllib.request


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA_ROOT = ROOT / "local/registros/F1-4G-SENSORES-20261021-01"
DATA = DATA_ROOT / "datos"
BASE = "http://10.133.182.55"
MESSAGE = "/mavlink2rest/v1/mavlink/vehicles/1/components/1/messages/"
DURATION = 300
WRITE_LOCK = threading.Lock()


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def append(name: str, value: dict, directory: pathlib.Path = DATA) -> None:
    row = {"utc": utc(), "mono": time.monotonic(), **value}
    with WRITE_LOCK:
        with (directory / f"{name}.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def get(url: str, timeout: float = 3) -> dict:
    start = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            raw = response.read()
            try:
                value = json.loads(raw)
            except ValueError:
                value = None
            return {"ok": response.status == 200, "status": response.status,
                    "elapsed_s": time.monotonic() - start, "value": value}
    except Exception as error:
        return {"ok": False, "elapsed_s": time.monotonic() - start,
                "error": type(error).__name__}


def counter(result: dict) -> int | None:
    try:
        return int(result["value"]["status"]["time"]["counter"])
    except (KeyError, TypeError, ValueError):
        return None


def message(result: dict) -> dict:
    return result.get("value", {}).get("message", {}) if result.get("ok") else {}


def gps_valid(gps: dict) -> bool:
    fix = gps.get("fix_type", {})
    name = fix.get("type", "") if isinstance(fix, dict) else str(fix)
    return name in {"GPS_FIX_TYPE_3D_FIX", "GPS_FIX_TYPE_DGPS",
                    "GPS_FIX_TYPE_RTK_FLOAT", "GPS_FIX_TYPE_RTK_FIXED", "3", "4", "5", "6"}


def armed(heartbeat: dict) -> bool | None:
    bits = heartbeat.get("base_mode", {}).get("bits")
    return bool(bits & 128) if isinstance(bits, int) else None


def ssh():
    # La importacion y lectura de credenciales suceden solo en preflight/capture reales.
    sys.path.insert(0, str(ROOT / "local/herramientas/ssh-paramiko"))
    import paramiko

    line = next(line for line in (ROOT / "local/credenciales.md").read_text(encoding="utf-8").splitlines()
                if re.search(r"SSH:", line, re.I))
    user, password = re.findall(r"`([^`]*)`", line)[:2]
    client = paramiko.SSHClient()
    client.load_system_host_keys(str(pathlib.Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("10.133.182.55", username=user, password=password,
                   look_for_keys=False, allow_agent=False, timeout=8,
                   banner_timeout=8, auth_timeout=8)
    return client


def remote_command(client, command: str, timeout: int = 15) -> dict:
    _, stdout, stderr = client.exec_command(command, timeout=timeout)
    return {"exit": stdout.channel.recv_exit_status(),
            "out": stdout.read().decode(errors="replace"),
            "err": stderr.read().decode(errors="replace")}


def preflight() -> dict:
    first = {name: get(BASE + MESSAGE + name) for name in ("HEARTBEAT", "GPS_RAW_INT")}
    time.sleep(1.2)
    second = {name: get(BASE + MESSAGE + name) for name in ("HEARTBEAT", "GPS_RAW_INT")}
    client = ssh()
    try:
        route = remote_command(client, "ip route get 1.1.1.1")
        links = remote_command(client, "ip -j link show eth1")
        statustext = remote_command(client, "curl -s --max-time 3 http://127.0.0.1" + MESSAGE + "STATUSTEXT")
        containers = remote_command(client, "docker ps --format '{{.Names}}'")
        zt = next((name for name in containers["out"].splitlines() if "zerotier" in name.lower()), None)
        zt_info = remote_command(client, "docker exec " + shlex.quote(zt) + " zerotier-cli info") if zt else None
    finally:
        client.close()
    hb = message(second["HEARTBEAT"])
    gps = message(second["GPS_RAW_INT"])
    conditions = {
        "heartbeat_fresh": counter(first["HEARTBEAT"]) is not None and
                           counter(second["HEARTBEAT"]) is not None and
                           counter(second["HEARTBEAT"]) > counter(first["HEARTBEAT"]),
        "disarmed": armed(hb) is False,
        "gps_valid": gps_valid(gps),
        "gps_fresh": counter(first["GPS_RAW_INT"]) is not None and
                     counter(second["GPS_RAW_INT"]) is not None and
                     counter(second["GPS_RAW_INT"]) > counter(first["GPS_RAW_INT"]),
        "mobile_route": route["exit"] == 0 and " dev eth1 " in " " + route["out"] + " ",
        "mobile_link": links["exit"] == 0 and "LOWER_UP" in links["out"],
        "zerotier_online": bool(zt_info and "ONLINE" in zt_info["out"]),
    }
    return {"utc": utc(), "first": first, "second": second, "route": route,
            "mobile_link": links, "latest_statustext": statustext,
            "zerotier": zt_info, "zt_container": zt, "conditions": conditions,
            "operator_checks": ["sin aviso vigente de brujula en Cockpit/BlueOS",
                                "posicion GPS plausible en el lugar",
                                "PC con Internet independiente de KAME y sin Ethernet al barco",
                                "Kame quieto, desarmado, supervisado y al aire libre",
                                "una sola reproduccion YOLO visible en la pestana habitual"]}


def write_preflight() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    result = preflight()
    path = DATA / ("preflight-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"conditions": result["conditions"],
                      "gps": {key: message(result["second"]["GPS_RAW_INT"]).get(key)
                              for key in ("fix_type", "satellites_visible", "h_acc", "lat", "lon")},
                      "latest_statustext": result["latest_statustext"]["out"],
                      "operator_checks": result["operator_checks"],
                      "evidence": str(path)}, indent=2, ensure_ascii=False))


REMOTE = r'''
import concurrent.futures, datetime, json, subprocess, threading, time, urllib.request
stop=time.monotonic()+DUR
lock=threading.Lock()
def emit(kind, **value):
 with lock: print(json.dumps({'kind':kind,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mono':time.monotonic(),**value}),flush=True)
def cmd(args,timeout=4):
 try:
  p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
  return {'exit':p.returncode,'out':p.stdout,'err':p.stderr}
 except Exception as error:return {'ok':False,'error':type(error).__name__}
def get(name):
 start=time.monotonic()
 try:
  with urllib.request.urlopen('http://127.0.0.1/mavlink2rest/v1/mavlink/vehicles/1/components/1/messages/'+name,timeout=2) as response:
   return {'ok':response.status==200,'elapsed_s':time.monotonic()-start,'value':json.load(response)}
 except Exception as error:return {'ok':False,'elapsed_s':time.monotonic()-start,'error':type(error).__name__}
def schedule(interval,fn):
 target=time.monotonic()
 while target<stop:
  try:fn()
  except Exception as error:emit('error',error=type(error).__name__)
  target+=interval
  if target<time.monotonic():target=time.monotonic()
  time.sleep(max(0,min(target,stop)-time.monotonic()))
def telemetry():
 for name in ('HEARTBEAT','GPS_RAW_INT'):
  emit('telemetry',name=name,result=get(name))
def internet():emit('internet_ping',result=cmd(['ping','-I','eth1','-c','1','-W','1','1.1.1.1']))
def resources():
 emit('resources',values={'route':cmd(['ip','route','get','1.1.1.1']),
  'links':cmd(['ip','-j','-s','link']),
  'zerotier':cmd(['docker','exec',ZT,'zerotier-cli','info']),
  'peers':cmd(['docker','exec',ZT,'zerotier-cli','peers'])})
emit('start',duration_s=DUR)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 jobs=[pool.submit(schedule,1,telemetry),pool.submit(schedule,1,internet),pool.submit(schedule,10,resources)]
 for job in jobs:job.result()
emit('complete')
'''


def ping(address: str) -> dict:
    start = time.monotonic()
    try:
        process = subprocess.run(["ping", "-n", "1", "-w", "1500", address],
                                 capture_output=True, timeout=4)
        raw = process.stdout.decode("cp850", errors="replace")
        match = re.search(r"(?:time|tiempo)[=<]\s*(\d+)\s*ms", raw, re.I)
        return {"ok": bool(match), "rtt_ms": int(match.group(1)) if match else None,
                "elapsed_s": time.monotonic() - start, "exit": process.returncode}
    except Exception as error:
        return {"ok": False, "elapsed_s": time.monotonic() - start,
                "error": type(error).__name__}


def periodic(name: str, interval: float, end: float, fn) -> None:
    target = end - DURATION
    while target < end:
        try:
            append(name, fn())
        except Exception as error:
            append(name, {"ok": False, "error": type(error).__name__})
        target += interval
        if target < time.monotonic():
            target = time.monotonic()
        time.sleep(max(0, min(target, end) - time.monotonic()))


def remote_capture(container: str, pc_end: float) -> None:
    client = None
    try:
        client = ssh()
        remaining = max(0, pc_end - time.monotonic())
        code = "ZT=" + repr(container) + "\nDUR=" + repr(remaining) + "\n" + REMOTE
        _, stdout, stderr = client.exec_command("python3 -u -c " + shlex.quote(code), timeout=330)
        for line in stdout:
            try:
                append("pi", json.loads(line))
            except ValueError:
                append("events", {"kind": "remote_output_invalid"})
        error = stderr.read().decode(errors="replace")
        if error:
            append("events", {"kind": "remote_stderr", "text": error[-2000:]})
        append("events", {"kind": "remote_exit", "exit": stdout.channel.recv_exit_status()})
    except Exception as error:
        append("events", {"kind": "remote_error", "error": type(error).__name__})
    finally:
        if client:
            client.close()


def capture(confirmed: bool) -> None:
    if not confirmed:
        raise SystemExit("Faltan las comprobaciones visuales y del enlace independiente; use --confirmar-condiciones.")
    if (DATA / "events.jsonl").exists():
        raise SystemExit("Esta sesion ya tiene una captura. Cree un ID nuevo; no se sobrescriben datos.")
    result = preflight()
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "preflight_capture.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    if not all(result["conditions"].values()):
        raise SystemExit("Preflight fallido. Consulte datos/preflight_capture.json; no se inicia la captura.")
    if not result["zt_container"]:
        raise SystemExit("No se encontro el contenedor ZeroTier.")
    start = time.monotonic()
    end = start + DURATION
    append("events", {"kind": "start", "duration_s": DURATION,
                      "conditions_confirmed_by_operator": True})
    tasks = [threading.Thread(target=remote_capture, args=(result["zt_container"], end))]
    for name in ("HEARTBEAT", "GPS_RAW_INT"):
        tasks.append(threading.Thread(target=periodic,
                                     args=("pc_" + name.lower(), 1, end,
                                           lambda name=name: get(BASE + MESSAGE + name))))
    tasks.extend([
        threading.Thread(target=periodic, args=("pc_ping_pi", 1, end,
                                                       lambda: ping("10.133.182.55"))),
        threading.Thread(target=periodic, args=("pc_ping_internet", 1, end,
                                                       lambda: ping("1.1.1.1"))),
        threading.Thread(target=periodic, args=("pc_blueos", 10, end,
                                                       lambda: get(BASE + "/"))),
    ])
    for task in tasks:
        task.start()
    print("CAPTURA INICIADA: observe Cockpit sin interrupcion. Cambie la escena al inicio y cada minuto.", flush=True)
    for minute in range(1, 6):
        time.sleep(max(0, start + minute * 60 - time.monotonic()))
        if minute < 5:
            print(f"MINUTO {minute}: cambie la escena y anote cualquier corte con el subcomando marca.", flush=True)
        else:
            print("MINUTO 5: cambie la escena una ultima vez y compruebe el estado final.", flush=True)
    for task in tasks:
        task.join(timeout=35)
    append("events", {"kind": "complete", "elapsed_s": time.monotonic() - start,
                      "threads_alive": sum(task.is_alive() for task in tasks)})
    print("CAPTURA COMPLETA. Registre las observaciones de Cockpit y ejecute resumen.", flush=True)


def rows(name: str, directory: pathlib.Path = DATA) -> list[dict]:
    path = directory / f"{name}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []


def stats(numbers: list[float]) -> dict | None:
    if not numbers:
        return None
    values = sorted(numbers)
    return {"n": len(values), "min": values[0], "median": values[len(values) // 2],
            "p95": values[math.ceil(len(values) * .95) - 1], "max": values[-1]}


def summarize(directory: pathlib.Path = DATA) -> dict:
    events = rows("events", directory)
    outcome = {"generated_utc": utc(), "duration_complete": any(r.get("kind") == "complete" and
               r.get("threads_alive") == 0 and r.get("elapsed_s", 0) >= DURATION for r in events),
               "events": events}
    for name in ("pc_ping_pi", "pc_ping_internet"):
        samples = rows(name, directory)
        good = [r for r in samples if r.get("ok")]
        outcome[name] = {"attempts": len(samples), "responses": len(good),
                         "missing_percent": 100 * (len(samples) - len(good)) / len(samples) if samples else None,
                         "rtt_ms": stats([r["rtt_ms"] for r in good])}
    for source in ("pc", "pi"):
        for name in ("heartbeat", "gps_raw_int"):
            if source == "pc":
                samples = rows("pc_" + name, directory)
            else:
                samples = [r["result"] | {"utc": r["utc"], "mono": r["mono"]}
                           for r in rows("pi", directory) if r.get("kind") == "telemetry" and
                           r.get("name", "").lower() == name]
            good = [r for r in samples if r.get("ok") and counter(r) is not None]
            changes = [r for index, r in enumerate(good)
                       if index == 0 or counter(r) != counter(good[index - 1])]
            gaps = [b["mono"] - a["mono"] for a, b in zip(changes, changes[1:])]
            outcome[source + "_" + name] = {"attempts": len(samples), "responses": len(good),
                "first_counter": counter(good[0]) if good else None,
                "last_counter": counter(good[-1]) if good else None,
                "distinct_updates": len(changes),
                "observed_update_gap_s": stats(gaps),
                "last_observed_update_age_s": good[-1]["mono"] - changes[-1]["mono"] if changes else None,
                "request_ms": stats([r["elapsed_s"] * 1000 for r in good])}
            if name == "gps_raw_int":
                fixes = [message(r).get("fix_type") for r in good]
                satellites = [message(r).get("satellites_visible") for r in good]
                accuracy = [message(r).get("h_acc") for r in good]
                outcome[source + "_" + name].update({"fixes": fixes,
                    "invalid_fix_samples": sum(not gps_valid(message(r)) for r in good),
                    "satellites": stats([s for s in satellites if isinstance(s, (int, float))]),
                    "satellite_series": satellites,
                    "horizontal_accuracy_mm": stats([a for a in accuracy if isinstance(a, (int, float))])})
    pi = rows("pi", directory)
    pings = [r for r in pi if r.get("kind") == "internet_ping"]
    mobile_rtts = [float(match.group(1)) for r in pings
                   if (match := re.search(r"time=([\d.]+)", r.get("result", {}).get("out", "")))]
    outcome["pi_mobile_ping"] = {"attempts": len(pings),
        "responses": sum(r.get("result", {}).get("exit") == 0 for r in pings),
        "rtt_ms": stats(mobile_rtts)}
    http = rows("pc_blueos", directory)
    outcome["blueos"] = {"attempts": len(http), "responses": sum(r.get("ok") for r in http),
                         "response_ms": stats([r["elapsed_s"] * 1000 for r in http if r.get("ok")])}
    resources = [r for r in pi if r.get("kind") == "resources"]
    outcome["resources"] = {"samples": len(resources),
        "routes": [r["values"]["route"].get("out", "").strip() for r in resources],
        "zerotier": [r["values"]["zerotier"].get("out", "").strip() for r in resources]}
    if resources:
        try:
            links = [json.loads(r["values"]["links"]["out"]) for r in (resources[0], resources[-1])]
            mobile = [next(x for x in group if x["ifname"] == "eth1")["stats64"] for group in links]
            outcome["mobile_interface_deltas"] = {direction: {key: mobile[1][direction][key] - mobile[0][direction][key]
                for key in mobile[0][direction]} for direction in ("rx", "tx")}
        except (KeyError, ValueError, StopIteration):
            outcome["mobile_interface_deltas"] = None
    marks = rows("marks", directory)
    outcome["browser_observation"] = {"marks": marks,
        "continuous_confirmed": any(r.get("kind") == "observacion_continua" for r in marks) and
                                not any(r.get("kind") == "observacion_interrumpida" for r in marks),
        "scene_marks": sum(r.get("kind") == "escena" for r in marks),
        "status": "evaluar observacion y marcas; API/HTTP no acreditan Cockpit ni imagen"}
    return outcome


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("--confirmar-condiciones", action="store_true")
    mark_parser = sub.add_parser("marca")
    mark_parser.add_argument("tipo", choices=("escena", "cockpit_desconectado", "modo_antiguo",
                                              "video_congelado", "retraso", "observacion_continua",
                                              "observacion_interrumpida", "otro"))
    mark_parser.add_argument("nota", nargs="?", default="")
    sub.add_parser("resumen")
    sub.add_parser("simular")
    args = parser.parse_args()
    if args.command == "preflight":
        write_preflight()
    elif args.command == "capture":
        capture(args.confirmar_condiciones)
    elif args.command == "marca":
        if not DATA.exists():
            raise SystemExit("No existe una sesion real.")
        append("marks", {"kind": args.tipo, "note": args.nota})
    elif args.command == "resumen":
        if not DATA.exists():
            raise SystemExit("No existe una sesion real.")
        result = summarize()
        (DATA / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Resumen privado: " + str(DATA / "summary.json"))
        print(json.dumps({"duration_complete": result["duration_complete"],
                          "pc_ping_pi": result["pc_ping_pi"],
                          "pc_heartbeat": result["pc_heartbeat"],
                          "pc_gps_raw_int": {key: result["pc_gps_raw_int"][key]
                                             for key in ("responses", "satellites", "horizontal_accuracy_mm")},
                          "browser_observation": {"continuous_confirmed": result["browser_observation"]["continuous_confirmed"],
                                                  "scene_marks": result["browser_observation"]["scene_marks"]}},
                         indent=2, ensure_ascii=False))
    elif args.command == "simular":
        compile("ZT='simulado'\nDUR=1\n" + REMOTE, "captura_remota", "exec")
        assert gps_valid({"fix_type": {"type": "GPS_FIX_TYPE_3D_FIX"}})
        assert not gps_valid({"fix_type": {"type": "GPS_FIX_TYPE_NO_FIX"}})
        assert armed({"base_mode": {"bits": 65}}) is False
        assert armed({"base_mode": {"bits": 193}}) is True
        DATA_ROOT.mkdir(parents=True, exist_ok=True)
        directory = DATA_ROOT / ("simulacion-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
        directory.mkdir()
        for number in range(6):
            for name in ("pc_ping_pi", "pc_ping_internet"):
                append(name, {"ok": True, "rtt_ms": 100 + number}, directory)
            for name in ("heartbeat", "gps_raw_int"):
                value = {"status": {"time": {"counter": number + 1}},
                         "message": {"fix_type": {"type": "GPS_FIX_TYPE_3D_FIX"},
                                     "satellites_visible": 12, "h_acc": 1200}}
                append("pc_" + name, {"ok": True, "elapsed_s": .1, "value": value}, directory)
            append("pi", {"kind": "telemetry", "name": "HEARTBEAT",
                          "result": {"ok": True, "elapsed_s": .01,
                                     "value": {"status": {"time": {"counter": number + 1}}, "message": {}}}}, directory)
            append("pi", {"kind": "telemetry", "name": "GPS_RAW_INT",
                          "result": {"ok": True, "elapsed_s": .01, "value": value}}, directory)
            append("pi", {"kind": "internet_ping", "result": {"exit": 0}}, directory)
            append("pc_blueos", {"ok": True, "status": 200, "elapsed_s": .2}, directory)
        link = [{"ifname": "eth1", "stats64": {"rx": {"errors": 10}, "tx": {"errors": 0}}}]
        for number in (0, 2):
            link[0]["stats64"]["rx"]["errors"] = 10 + number
            append("pi", {"kind": "resources", "values": {
                "route": {"out": "via modem dev eth1"},
                "links": {"out": json.dumps(link)},
                "zerotier": {"out": "ONLINE"}}}, directory)
        append("events", {"kind": "complete", "threads_alive": 0,
                          "elapsed_s": DURATION}, directory)
        result = summarize(directory)
        assert result["duration_complete"] is True
        assert result["pc_heartbeat"]["last_counter"] == 6
        assert result["pc_gps_raw_int"]["satellites"]["min"] == 12
        assert result["browser_observation"]["continuous_confirmed"] is False
        assert result["mobile_interface_deltas"]["rx"]["errors"] == 2
        result["simulation"] = True
        (directory / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print("SIMULACION OK: datos ficticios; sin red, barco, credenciales ni cambios operativos.")


if __name__ == "__main__":
    main()
