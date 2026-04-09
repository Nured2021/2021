from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "odex-secret"
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# IMPORT REAL SYSTEM ENTRY
from orchestrator import run_orchestrator

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "system": "ODEX",
        "mode": "standalone",
        "engines": "57+"
    })

@app.route("/api/run", methods=["POST"])
def run_api():
    data = request.json or {}
    prompt = data.get("message", "")
    result = run_orchestrator(prompt)
    return jsonify(result)

@socketio.on("connect")
def on_connect():
    emit("log", {"type": "system", "status": "CONNECTED", "message": "ODEX backend connected"})

@socketio.on("run_engine")
def handle_run(data):
    prompt = data.get("message", "")
    emit("log", {"type": "system", "status": "START", "message": prompt})
    try:
        result = run_orchestrator(prompt, socketio=socketio)
        emit("log", {"type": "system", "status": "DONE", "result": result})
    except Exception as e:
        emit("log", {"type": "system", "status": "ERROR", "message": str(e)})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)







