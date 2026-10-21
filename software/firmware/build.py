#!/usr/bin/env python3
"""Build the pinned Navigator64 Rover fix locally. Never connects to a vehicle."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE = "fb773567896014da007bca58358704d4a0d8516f"
REPOSITORY = "https://github.com/ArduPilot/ardupilot.git"


def run(args, cwd, env=None, capture=False):
    return subprocess.run(args, cwd=cwd, env=env, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    work = (ROOT / "local/firmware").resolve()
    source = work / "ardupilot"
    venv = work / "venv"
    output = work / "artifacts/navigator64-pi5-pwm"
    work.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    local_tools = work / "toolchain/root/usr/bin"
    env["PATH"] = os.pathsep.join([str(venv / "bin"), str(local_tools), env["PATH"]])
    local_libraries = work / "toolchain/root/usr/lib/x86_64-linux-gnu"
    if local_libraries.is_dir():
        env["LD_LIBRARY_PATH"] = os.pathsep.join(
            [str(local_libraries)] + ([env["LD_LIBRARY_PATH"]] if env.get("LD_LIBRARY_PATH") else []))
        sysroot = shlex.quote("--sysroot=" + str(work / "toolchain/root"))
        for flag in ("CFLAGS", "CXXFLAGS", "LINKFLAGS"):
            env[flag] = (env.get(flag, "") + " " + sysroot).strip()
    compiler = shutil.which("aarch64-linux-gnu-g++", path=env["PATH"])
    if not compiler:
        sys.exit("GCC 11 cross compiler missing; see this component's README.")
    if run([compiler, "-dumpversion"], work, env, True).strip().split(".")[0] != "11":
        sys.exit("This recipe requires GCC 11 for aarch64-linux-gnu.")
    if not source.exists():
        run(["git", "clone", "--filter=blob:none", "--no-checkout", "--depth=1",
             REPOSITORY, str(source)], work)
        run(["git", "fetch", "--depth=1", "origin", BASE], source)
        run(["git", "checkout", "--detach", BASE], source)
    head = run(["git", "rev-parse", "HEAD"], source, capture=True).strip()
    if head != BASE:
        if run(["git", "status", "--porcelain", "--untracked-files=no"], source, capture=True).strip():
            sys.exit("Source checkout has unrelated changes; preserve them before selecting the pinned base.")
        run(["git", "fetch", "--depth=1", "origin", BASE], source)
        run(["git", "checkout", "--detach", BASE], source)
    patch = HERE / "navigator-pi5-pwm.patch"
    already = subprocess.run(["git", "apply", "--reverse", "--check", str(patch)],
                             cwd=source, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    if not already:
        if run(["git", "diff", "--name-only"], source, capture=True).strip():
            sys.exit("Refusing to patch a modified source checkout.")
        run(["git", "apply", "--check", str(patch)], source)
        run(["git", "apply", str(patch)], source)
    # Refuse extra modifications, including edits elsewhere in the same file.
    if run(["git", "diff", "--cached", "--name-only"], source, capture=True).strip():
        sys.exit("Refusing staged source changes.")
    if run(["git", "ls-files", "--others", "--exclude-standard"], source, capture=True).strip():
        sys.exit("Refusing untracked source files.")
    changed = run(["git", "diff", "--name-only"], source, capture=True).splitlines()
    if changed != ["libraries/AP_HAL_Linux/HAL_Linux_Class.cpp"]:
        sys.exit("Unexpected source changes; only the PWM selector is allowed.")
    original = run(["git", "show", BASE + ":" + changed[0]], source, capture=True)
    patch_lines = patch.read_text().splitlines()
    removed = "\n".join(line[1:] for line in patch_lines if line.startswith("-") and not line.startswith("---")) + "\n"
    added = "\n".join(line[1:] for line in patch_lines if line.startswith("+") and not line.startswith("+++")) + "\n"
    if original.count(removed) != 1 or (source / changed[0]).read_text() != original.replace(removed, added, 1):
        sys.exit("Source does not match exactly the pinned base plus this patch.")
    run(["git", "submodule", "update", "--init", "--recursive", "--depth=1", "--jobs=4"], source)
    submodules = run(["git", "submodule", "status", "--recursive"], source, capture=True).splitlines()
    if any(not line.startswith(" ") for line in submodules):
        sys.exit("Submodule revisions do not match the pinned source.")
    if not (venv / "bin/python").exists():
        run([sys.executable, "-m", "venv", str(venv)], work)
    python = str(venv / "bin/python")
    run([python, "-m", "pip", "install", "-r", str(HERE / "requirements-build.txt")], work, env)
    run([python, "waf", "configure", "--board", "navigator64", "--toolchain", "aarch64-linux-gnu"], source, env)
    run([python, "waf", "rover", "-j", str(args.jobs)], source, env)
    binary = source / "build/navigator64/bin/ardurover"
    output.mkdir(parents=True, exist_ok=True)
    artifact = output / "ardurover"
    shutil.copy2(binary, artifact)
    manifest = {
        "utc": datetime.now(timezone.utc).isoformat(), "kind": "local patched build, not official binary",
        "base_commit": BASE, "board": "navigator64", "vehicle": "Rover", "version": "4.7.2",
        "patch_sha256": digest(patch), "binary_sha256": digest(artifact), "binary_size": artifact.stat().st_size,
        "modified_source_sha256": digest(source / changed[0]),
        "toolchain_packages": {p.name: digest(p) for p in sorted((work / "toolchain/debs").glob("*.deb"))},
        "compiler": run([compiler, "--version"], work, env, True).splitlines()[0],
        "python": run([python, "--version"], work, env, True).strip(),
        "environment_flags": {key: env.get(key, "") for key in ("CFLAGS", "CXXFLAGS", "LINKFLAGS")},
        "submodules": submodules,
        "source_diff": run(["git", "diff", "--no-ext-diff"], source, capture=True),
        "pip_freeze": run([python, "-m", "pip", "freeze"], work, env, True).splitlines(),
        "configure": "./waf configure --board navigator64 --toolchain aarch64-linux-gnu",
        "build": f"./waf rover -j {args.jobs}",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"artifact": str(artifact), "sha256": manifest["binary_sha256"]}))


if __name__ == "__main__":
    main()
