import subprocess
import sys
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "app.py"
LOG_FILE = ROOT / "auto_master_fixer.log"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def run_backend():
    try:
        process = subprocess.run(
            [sys.executable, str(APP_FILE)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20
        )
        return process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired:
        return 0, "Backend stayed alive long enough (timeout success assumption).", ""

def install_package(package_name):
    log(f"[INSTALL] Installing missing package: {package_name}")
    subprocess.run([sys.executable, "-m", "pip", "install", package_name], cwd=str(ROOT))

def fix_missing_init(target_file):
    folder = Path(target_file).parent
    init_file = folder / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")
        log(f"[FIX] Added missing __init__.py in {folder}")

def fix_import_error(stderr):
    match = re.search(r"No module named ['\"]([^'\"]+)['\"]", stderr)
    if not match:
        return False
    missing = match.group(1)

    # Try installing likely package if external
    if "." not in missing and missing not in {"engine", "brains", "memory", "queue", "storage"}:
        install_package(missing)
        return True

    log(f"[WARN] Missing internal module detected: {missing}")
    return False

def fix_syntax_error(stderr):
    match = re.search(r'File "([^"]+)", line (\d+)', stderr)
    if not match:
        return False
    file_path = Path(match.group(1))
    line_no = int(match.group(2))
    log(f"[WARN] Syntax issue detected in {file_path} line {line_no}")
    return False

def fix_relative_imports(stderr):
    if "attempted relative import" in stderr or "ImportError" in stderr:
        log("[WARN] Relative import issue detected. Check app.py, orchestrator.py, main_engine.py imports.")
        return False
    return False

def main():
    log("=== ODEX AUTO MASTER FIXER START ===")
    max_rounds = 10

    for attempt in range(1, max_rounds + 1):
        log(f"\n[ATTEMPT {attempt}] Running backend boot test...")
        code, out, err = run_backend()

        if out:
            log("[STDOUT]")
            log(out)

        if err:
            log("[STDERR]")
            log(err)

        success_signals = [
            "Running on http://127.0.0.1:5000",
            "Running on http://0.0.0.0:5000",
            "Serving Flask app",
            "Backend stayed alive long enough"
        ]

        if code == 0 and any(signal in out for signal in success_signals):
            log("[SUCCESS] ODEX backend appears to be running.")
            return

        fixed = False

        if "No module named" in err:
            fixed = fix_import_error(err) or fixed

        if "SyntaxError" in err:
            fixed = fix_syntax_error(err) or fixed

        if "ImportError" in err or "attempted relative import" in err:
            fixed = fix_relative_imports(err) or fixed

        if not fixed:
            log("[STOP] Automatic fixer could not safely patch this error.")
            log("Open app.py, orchestrator.py, and main_engine.py and repair the exact failing import or syntax issue.")
            return

    log("[FAIL] Max attempts reached without standing backend.")

if __name__ == "__main__":
    main()






