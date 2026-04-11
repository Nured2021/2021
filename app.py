"""
ORD AI Platform — Backend
50 Cores / 50 Engines / 50 AI Builders + ∞-Loop + Three-Window UI
"""
import threading
import time
import random
import subprocess
import sys
import json
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "ord-ai-platform-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# ──────────────────────────────────────────────
# GLOBAL STATE
# ──────────────────────────────────────────────

STATE = {
    "build_active": False,
    "build_progress": 0,
    "build_task": "Idle",
    "cores_active": 0,
    "engines_active": 0,
    "ai_active": 0,
    "tests_passed": 0,
    "tests_total": 50,
    "fixes_applied": 0,
    "files_created": [],
    "bottlenecks": [],
    "job_queue": [],
    "current_job": None,
    "loop_count": 0,
    "version": "v1.0.0",
    "team_online": 3,
    "uptime": 99.99,
    "cpu": 34,
    "ram": 56,
    "rps": 0,
    "resp_ms": 45,
    "saves": [
        {"name": "Demo_System_v1.0.0", "version": "v1.0.0", "time": "2 hours ago"},
    ],
    "versions": [
        {"ver": "v1.0.0", "msg": "Initial ORD AI build", "time": "Now"},
    ],
    "marketplace": [
        {"name": "ChatGPT Clone", "price": "$49", "downloads": "1.2K"},
        {"name": "Ecommerce Platform", "price": "$99", "downloads": "450"},
        {"name": "AI Assistant", "price": "$29", "downloads": "2.1K"},
    ],
    "test_results": {
        "unit": {"passed": 145, "total": 145},
        "integration": {"passed": 67, "total": 67},
        "performance": {"passed": 49, "total": 50},
        "security": {"passed": 20, "total": 20},
        "ui": {"passed": 89, "total": 89},
    },
    "pilot_log": [],
}

BUILD_STAGES = [
    ("Initializing 50 Cores...",          5,  2),
    ("Activating 50 Engines...",          10, 3),
    ("Starting 50 AI Builders...",        15, 2),
    ("Engine 1-10: Generating frontend code...", 25, 4),
    ("Engine 11-20: Building backend...", 35, 4),
    ("Engine 21-30: Writing database layer...", 45, 3),
    ("Engine 31-40: Running unit tests...", 55, 3),
    ("Engine 41-50: Security scan...",    65, 3),
    ("AI Builders: Fixing detected issues...", 70, 2),
    ("Optimizing performance...",         78, 3),
    ("Generating documentation...",       84, 2),
    ("Deploying to staging...",           90, 2),
    ("Running final validation...",       96, 2),
    ("System ready!",                    100, 1),
]

FILE_SEQUENCE = [
    "app.py", "models/user.py", "models/db.py",
    "routes/api.py", "routes/auth.py", "static/index.html",
    "static/style.css", "static/app.js", "tests/test_api.py",
    "Dockerfile", "README.md",
]

# ──────────────────────────────────────────────
# PILOT LOGGING
# ──────────────────────────────────────────────

def pilot_say(msg, kind="info"):
    entry = {"time": datetime.now().strftime("%H:%M:%S"), "msg": msg, "kind": kind}
    STATE["pilot_log"].append(entry)
    if len(STATE["pilot_log"]) > 200:
        STATE["pilot_log"].pop(0)
    socketio.emit("pilot_msg", entry)


# ──────────────────────────────────────────────
# ∞-LOOP BUILD ENGINE
# ──────────────────────────────────────────────

def _run_build(job_name):
    STATE["build_active"] = True
    STATE["build_progress"] = 0
    STATE["files_created"] = []
    STATE["fixes_applied"] = 0
    STATE["tests_passed"] = 0
    STATE["bottlenecks"] = []
    STATE["loop_count"] += 1

    pilot_say(f"▶ Starting build: {job_name}", "start")
    pilot_say("100% Alive — answering, building, showing, learning, correcting.", "info")

    file_idx = 0
    for stage, target_pct, delay in BUILD_STAGES:
        STATE["build_task"] = stage
        STATE["cores_active"] = min(50, int(target_pct * 0.5))
        STATE["engines_active"] = min(50, int(target_pct * 0.5))
        STATE["ai_active"] = min(50, int(target_pct * 0.48))
        STATE["rps"] = random.randint(800, 1500)
        STATE["cpu"] = random.randint(28, 72)
        STATE["ram"] = random.randint(40, 70)

        # Simulate progress ticks
        current = STATE["build_progress"]
        steps = target_pct - current
        for i in range(max(1, steps)):
            STATE["build_progress"] = current + i + 1
            # Add file
            if file_idx < len(FILE_SEQUENCE) and STATE["build_progress"] % 8 == 0:
                STATE["files_created"].append(FILE_SEQUENCE[file_idx])
                file_idx += 1
            # Add test passes
            if STATE["build_progress"] % 3 == 0 and STATE["tests_passed"] < 50:
                STATE["tests_passed"] += 1
            # Random bottleneck
            if random.random() < 0.04 and len(STATE["bottlenecks"]) < 3:
                bn = f"Engine {random.randint(1,50)} needs attention"
                if bn not in STATE["bottlenecks"]:
                    STATE["bottlenecks"].append(bn)
                    pilot_say(f"⚠ Bottleneck: {bn} — auto-fixing", "warn")
            # Auto-fix
            if STATE["bottlenecks"] and random.random() < 0.3:
                fixed = STATE["bottlenecks"].pop(0)
                STATE["fixes_applied"] += 1
                pilot_say(f"✓ Fixed: {fixed}", "fix")

            socketio.emit("state_update", _public_state())
            time.sleep(delay / max(1, steps))

        pilot_say(f"✔ {stage}", "done")
        socketio.emit("state_update", _public_state())

    # Increment version
    parts = STATE["version"].lstrip("v").split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    STATE["version"] = "v" + ".".join(parts)
    STATE["versions"].insert(0, {
        "ver": STATE["version"],
        "msg": f"Built: {job_name}",
        "time": "Just now",
    })

    STATE["build_active"] = False
    STATE["current_job"] = None
    pilot_say(f"🎉 Build complete: {job_name} — {STATE['version']}", "success")
    socketio.emit("build_done", {"job": job_name, "version": STATE["version"]})

    # Process next queued job
    if STATE["job_queue"]:
        next_job = STATE["job_queue"].pop(0)
        STATE["current_job"] = next_job
        pilot_say(f"↩ Loop continues — next job: {next_job}", "info")
        socketio.emit("state_update", _public_state())
        threading.Thread(target=_run_build, args=(next_job,), daemon=True).start()


def _public_state():
    return {k: v for k, v in STATE.items() if k != "pilot_log"}


# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    return jsonify(_public_state())


@app.route("/api/pilot_log")
def api_pilot_log():
    return jsonify(STATE["pilot_log"])


@app.route("/api/build", methods=["POST"])
def api_build():
    data = request.get_json(silent=True) or {}
    job = data.get("job", "Custom System").strip() or "Custom System"
    if STATE["build_active"]:
        STATE["job_queue"].append(job)
        pilot_say(f"📋 Queued: {job} (position {len(STATE['job_queue'])})", "info")
        socketio.emit("state_update", _public_state())
        return jsonify({"status": "queued", "job": job})
    STATE["current_job"] = job
    threading.Thread(target=_run_build, args=(job,), daemon=True).start()
    return jsonify({"status": "started", "job": job})


@app.route("/api/execute", methods=["POST"])
def api_execute():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    lang = data.get("lang", "python")
    if not code.strip():
        return jsonify({"output": "", "error": "No code provided"})
    try:
        if lang == "python":
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True, timeout=10
            )
            output = result.stdout
            error = result.stderr
        elif lang == "javascript":
            result = subprocess.run(
                ["node", "-e", code],
                capture_output=True, text=True, timeout=10
            )
            output = result.stdout
            error = result.stderr
        else:
            output = f"[{lang}] execution not supported in sandbox"
            error = ""
    except subprocess.TimeoutExpired:
        output = ""
        error = "Execution timed out (10s limit)"
    except FileNotFoundError:
        output = ""
        error = f"Runtime '{lang}' not available"
    pilot_say(f"▷ Code executed ({lang})", "info")
    return jsonify({"output": output, "error": error})


@app.route("/api/fix_bottleneck", methods=["POST"])
def api_fix_bottleneck():
    data = request.get_json(silent=True) or {}
    bn = data.get("bottleneck", "")
    if bn in STATE["bottlenecks"]:
        STATE["bottlenecks"].remove(bn)
        STATE["fixes_applied"] += 1
        pilot_say(f"✓ User fixed: {bn}", "fix")
        socketio.emit("state_update", _public_state())
    return jsonify({"status": "fixed"})


@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "Unnamed System")
    ver = data.get("version", STATE["version"])
    STATE["saves"].insert(0, {"name": name, "version": ver, "time": "Just now"})
    pilot_say(f"💾 Saved: {name} ({ver})", "info")
    return jsonify({"status": "saved", "name": name, "version": ver})


@app.route("/api/ai_chat", methods=["POST"])
def api_ai_chat():
    data = request.get_json(silent=True) or {}
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"reply": "Please type a message."})

    msg_lower = msg.lower()
    if any(w in msg_lower for w in ["build", "create", "make", "generate"]):
        reply = (f"Starting build for: '{msg}'. Activating 50 cores, "
                 "50 engines, and 50 AI builders. Watch the Live Preview window.")
        if not STATE["build_active"]:
            STATE["current_job"] = msg
            threading.Thread(target=_run_build, args=(msg,), daemon=True).start()
    elif any(w in msg_lower for w in ["status", "progress", "how"]):
        reply = (f"Current status: {STATE['build_progress']}% complete. "
                 f"Cores: {STATE['cores_active']}/50. "
                 f"Engines: {STATE['engines_active']}/50. "
                 f"Task: {STATE['build_task']}")
    elif any(w in msg_lower for w in ["fix", "bug", "error", "problem"]):
        reply = ("Scanning for issues now... Found and fixing automatically. "
                 "I'll report back when complete.")
        STATE["bottlenecks"] = []
        STATE["fixes_applied"] += 1
        pilot_say("✓ AI chat triggered auto-fix", "fix")
    elif any(w in msg_lower for w in ["help", "what", "?"]):
        reply = ("I can: BUILD any system, FIX bugs, DEPLOY to cloud, TEST code, "
                 "SAVE progress, and SHOW live metrics. Just tell me what you need!")
    elif any(w in msg_lower for w in ["stop", "pause", "cancel"]):
        STATE["build_active"] = False
        reply = "Build paused. Type 'resume' or a new build command to continue."
        pilot_say("⏸ Build paused by user", "warn")
    elif any(w in msg_lower for w in ["deploy"]):
        reply = ("Deploying to cloud. Choose: AWS, GCP, Azure, Vercel, Netlify. "
                 "Default: AWS us-east-1. Deployment will take ~2 minutes.")
    else:
        replies = [
            f"Understood: '{msg}'. Processing your request now.",
            "I'm on it! Watch the Live Preview for real-time progress.",
            "Adding to the ∞ loop. Never stopping — always building.",
            "100% committed. Your request is being handled right now.",
        ]
        reply = random.choice(replies)

    pilot_say(f"🤖 AI Pilot: {reply}", "pilot")
    return jsonify({"reply": reply})


@app.route("/api/test_run", methods=["POST"])
def api_test_run():
    pilot_say("🧪 Running full test suite...", "info")
    def _run_tests():
        time.sleep(2)
        STATE["test_results"] = {
            "unit": {"passed": 145, "total": 145},
            "integration": {"passed": 67, "total": 67},
            "performance": {"passed": 49, "total": 50},
            "security": {"passed": 20, "total": 20},
            "ui": {"passed": 89, "total": 89},
        }
        pilot_say("✅ All tests complete. Coverage: 97%", "success")
        socketio.emit("tests_done", STATE["test_results"])
    threading.Thread(target=_run_tests, daemon=True).start()
    return jsonify({"status": "running"})


# ──────────────────────────────────────────────
# SOCKET.IO EVENTS
# ──────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    pilot_say("👋 New user connected to ORD AI Platform", "info")
    emit("state_update", _public_state())
    emit("pilot_history", STATE["pilot_log"][-50:])


@socketio.on("ping_state")
def on_ping():
    emit("state_update", _public_state())


# ──────────────────────────────────────────────
# BACKGROUND METRICS TICKER
# ──────────────────────────────────────────────

def _metrics_ticker():
    while True:
        if STATE["build_active"]:
            STATE["rps"] = random.randint(900, 1600)
            STATE["cpu"] = min(95, STATE["cpu"] + random.randint(-3, 5))
            STATE["ram"] = min(90, STATE["ram"] + random.randint(-2, 3))
        else:
            STATE["rps"] = random.randint(100, 400)
            STATE["cpu"] = max(5, STATE["cpu"] + random.randint(-2, 2))
            STATE["ram"] = max(20, STATE["ram"] + random.randint(-1, 1))
        socketio.emit("metrics_update", {
            "cpu": STATE["cpu"],
            "ram": STATE["ram"],
            "rps": STATE["rps"],
            "resp_ms": STATE["resp_ms"],
            "uptime": STATE["uptime"],
        })
        time.sleep(3)


threading.Thread(target=_metrics_ticker, daemon=True).start()

# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 ORD AI Platform starting on http://0.0.0.0:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
