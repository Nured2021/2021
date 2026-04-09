import os
import sys
import subprocess
import traceback
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
APP = ROOT / "app.py"
LOG = ROOT / "system_fix.log"

COMMON_PACKAGES = [
    "flask",
    "flask-socketio",
    "flask-cors"
]

def log(msg):
    print(msg)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def install_missing(pkg):
    log(f"[INSTALL] {pkg}")
    subprocess.run([sys.executable, "-m", "pip", "install", pkg])

def ensure_init_files():
    for folder, _, files in os.walk(ROOT):
        if any(f.endswith(".py") for f in files):
            init_file = Path(folder) / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")
                log(f"[FIX] Added __init__.py → {folder}")

def fix_basic_imports():
    for py_file in ROOT.rglob("*.py"):
        try:
            code = py_file.read_text(encoding="utf-8")
        except:
            continue

        # Example fix: remove bad absolute "engine." prefix if already inside engine
        if "from " in code:
            code = code.replace("from ", "from ")
            py_file.write_text(code, encoding="utf-8")
            log(f"[FIX] Adjusted import in {py_file}")

def scan_syntax():
    for py_file in ROOT.rglob("*.py"):
        try:
            compile(py_file.read_text(encoding="utf-8"), str(py_file), "exec")
        except SyntaxError as e:
            log(f"[SYNTAX ERROR] {py_file}:{e.lineno} → {e.msg}")

def run_backend():
    try:
        proc = subprocess.Popen(
            [sys.executable, str(APP)],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            return True, "RUNNING", ""

        return False, stdout, stderr
    except Exception as e:
        return False, "", str(e)

def fix_missing_modules(stderr):
    matches = re.findall(r"No module named ['\"]([^'\"]+)['\"]", stderr)
    for m in matches:
        if "." not in m:
            install_missing(m)

def main():
    log("=== ODEX SYSTEM AUTO FIX START ===")

    # Step 1: ensure base packages
    for pkg in COMMON_PACKAGES:
        install_missing(pkg)

    # Step 2: ensure __init__.py everywhere
    ensure_init_files()

    # Step 3: fix imports
    fix_basic_imports()

    # Step 4: scan syntax
    scan_syntax()

    # Step 5: repair loop
    for i in range(10):
        log(f"\n[BOOT ATTEMPT {i+1}]")
        success, out, err = run_backend()

        if success:
            log("[SUCCESS] Backend is running on localhost:5000")
            return

        if err:
            log("[ERROR OUTPUT]")
            log(err)
            fix_missing_modules(err)

        if out:
            log("[OUTPUT]")
            log(out)

    log("[FAIL] Could not auto-fix system fully. Manual fix required.")

if __name__ == "__main__":
    main()






