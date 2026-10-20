"""Comprobaciones portátiles, sin dependencias Python externas ni acceso al barco."""

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]


def command(*args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, text=True, encoding="utf-8", **kwargs)


def repository_files():
    result = command("git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", capture_output=True)
    return sorted({ROOT / name for name in result.stdout.split("\0") if name and (ROOT / name).is_file()})


def headings(text):
    anchors = set()
    counts = {}
    for line in re.sub(r"```.*?```", "", text, flags=re.S).splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            slug = re.sub(r"[^\w\- ]", "", match[1].lower()).replace(" ", "-")
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def check_text(files):
    known_secrets = []
    private = ROOT / "local/credenciales.md"
    if private.exists():
        private_text = private.read_text(encoding="utf-8")
        for pattern in (r"contraseña `([^`]+)`", r"PIN `([^`]+)`"):
            match = re.search(pattern, private_text)
            if match:
                known_secrets.append(match[1])
    secret_pattern = re.compile(
        r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"
        r"|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}"
        r"|(?i:\b(?:password|passwd|sim_pin)\s*[:=]\s*['\"][^'\"\r\n]{4,}['\"])"
    )
    links = 0
    for path in files:
        relative = path.relative_to(ROOT)
        assert relative.parts[0] != "local", f"Archivo privado seleccionado: {relative}"
        assert path.stat().st_size < 1_000_000, f"Archivo pesado seleccionado: {relative}"
        text = path.read_text(encoding="utf-8")
        assert not secret_pattern.search(text), f"Posible secreto: {relative}"
        for value in known_secrets:
            assert not re.search(r"(?<![A-Za-z0-9])" + re.escape(value) + r"(?![A-Za-z0-9])", text), f"Credencial conocida: {relative}"
        if path.suffix == ".py":
            ast.parse(text, filename=str(relative))
        elif path.suffix in (".json", ".cmp", ".conf"):
            json.loads(text)
        elif path.suffix == ".mjs":
            command("node", "--check", str(path), capture_output=True)
        elif path.suffix == ".html":
            for script in re.findall(r"<script\b[^>]*>(.*?)</script>", text, flags=re.S | re.I):
                command("node", "--check", "--input-type=module", input=script, capture_output=True)
        elif path.suffix == ".sh" and sys.platform != "win32":
            command("bash", "-n", str(path), capture_output=True)
        if path.suffix != ".md":
            continue
        assert not re.search(r"\ufffd|\u00c3[\u0080-\u00bf]|\u00e2\u20ac", text), f"Codificación dañada: {relative}"
        assert text.count("```") % 2 == 0, f"Bloque de código abierto: {relative}"
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        for href in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", prose):
            href = href.strip().strip("<>")
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            assert target.is_relative_to(ROOT), f"Enlace fuera del repositorio: {relative}"
            assert target.exists(), f"Enlace inexistente: {relative} -> {href}"
            assert target.relative_to(ROOT).parts[0] != "local", f"Enlace privado no portable: {relative}"
            if parts.fragment:
                assert target.suffix == ".md" and unquote(parts.fragment) in headings(target.read_text(encoding="utf-8")), f"Ancla inexistente: {relative} -> {href}"
            links += 1
    print(f"OK: {len(files)} archivos, sintaxis/configuración, {links} enlaces/anclas y patrones de secretos")


def check_missions():
    with tempfile.TemporaryDirectory(prefix="kame-missions-") as directory:
        output = Path(directory) / "generated"
        subprocess.run([sys.executable, str(ROOT / "misiones/generate_missions.py"), "--output-dir", str(output)], cwd=directory, check=True)
        expected = ROOT / "misiones/cockpit"
        assert {p.name for p in output.iterdir()} == {p.name for p in expected.glob("*.cmp")}
        for original in expected.glob("*.cmp"):
            assert original.read_text(encoding="utf-8") == (output / original.name).read_text(encoding="utf-8"), f"Misión diferente: {original.name}"
    print("OK: misiones regeneradas equivalentes desde otro directorio de trabajo")


def main():
    if sys.version_info < (3, 12):
        raise SystemExit("Se necesita Python 3.12 o posterior")
    assert shutil.which("git") and shutil.which("node"), "Se necesitan Git y Node.js 20+"
    version = command("node", "--version", capture_output=True).stdout.strip()
    assert int(version.lstrip("v").split(".")[0]) >= 20, "Se necesita Node.js 20+"
    check_text(repository_files())
    check_missions()
    command("node", str(ROOT / ".github/checks/check_viewer.mjs"))
    print("OK: comprobaciones portátiles terminadas; no se consultó el vehículo")


if __name__ == "__main__":
    main()
