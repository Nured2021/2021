"""
EASY AI DOC & EDUCATION CORE
Full-stack platform: Document + Excel + Presentation + Education generation
"""
import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO

from engines.master_brain import route, detect_professor
from engines.document_engine import generate_pdf, generate_docx
from engines.excel_engine import generate_xlsx
from engines.presentation_engine import generate_pptx
from engines.education_engine import get_all_professors, generate_course, PROFESSORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "easy-ai-doc-2024"
socketio = SocketIO(app, cors_allowed_origins="*")

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Pages ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ── Master Brain Route ────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    result = route(prompt)
    return jsonify(result)

# ── Generate Documents ────────────────────────────────────────

@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    file_type = (data.get("type") or "pdf").lower()
    mode = data.get("mode", "formal")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        if file_type == "pdf":
            filename = generate_pdf(prompt, mode)
        elif file_type == "docx":
            filename = generate_docx(prompt, mode)
        elif file_type == "xlsx":
            filename = generate_xlsx(prompt)
        elif file_type == "pptx":
            filename = generate_pptx(prompt)
        else:
            return jsonify({"error": f"Unsupported type: {file_type}"}), 400

        return jsonify({
            "status": "success",
            "filename": filename,
            "type": file_type,
            "download_url": f"/download/{filename}",
            "generated_at": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Smart Generate (auto-detect) ─────────────────────────────

@app.route("/api/smart-generate", methods=["POST"])
def api_smart_generate():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    analysis = route(prompt)
    results = []

    for ft in analysis["file_types"]:
        try:
            if ft == "pdf":
                fn = generate_pdf(prompt, analysis["mode"])
            elif ft == "docx":
                fn = generate_docx(prompt, analysis["mode"])
            elif ft == "xlsx":
                fn = generate_xlsx(prompt)
            elif ft == "pptx":
                fn = generate_pptx(prompt)
            else:
                continue
            results.append({"type": ft, "filename": fn, "download_url": f"/download/{fn}"})
        except Exception as e:
            results.append({"type": ft, "error": str(e)})

    return jsonify({
        "status": "success",
        "analysis": analysis,
        "files": results,
        "generated_at": datetime.now().isoformat(),
    })

# ── Education ─────────────────────────────────────────────────

@app.route("/api/professors")
def api_professors():
    return jsonify(get_all_professors())

@app.route("/api/education/generate", methods=["POST"])
def api_edu_generate():
    data = request.get_json(silent=True) or {}
    professor_id = data.get("professor", "cs")
    topic = (data.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "No topic provided"}), 400
    if professor_id not in PROFESSORS:
        return jsonify({"error": f"Unknown professor: {professor_id}"}), 400

    course = generate_course(professor_id, topic)
    return jsonify({"status": "success", "course": course})

# ── Downloads ─────────────────────────────────────────────────

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

@app.route("/api/files")
def api_files():
    files = []
    for f in sorted(os.listdir(DOWNLOAD_DIR), reverse=True):
        fpath = os.path.join(DOWNLOAD_DIR, f)
        ext = f.rsplit(".", 1)[-1] if "." in f else ""
        files.append({
            "name": f,
            "type": ext,
            "size": os.path.getsize(fpath),
            "download_url": f"/download/{f}",
            "created": datetime.fromtimestamp(os.path.getctime(fpath)).isoformat(),
        })
    return jsonify(files)

# ── Health ────────────────────────────────────────────────────

@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "engines": ["document", "excel", "presentation", "education"],
        "professors": len(PROFESSORS),
        "timestamp": datetime.now().isoformat(),
    })

# ── WebSocket ─────────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    socketio.emit("welcome", {"msg": "Connected to EASY AI DOC & EDUCATION CORE"})

# ── Entry ─────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("\n" + "=" * 60)
    print("  EASY AI DOC & EDUCATION CORE")
    print("  Document | Excel | Presentation | 20 AI Professors")
    print(f"  Open in browser -> http://localhost:{port}")
    print("=" * 60 + "\n")
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
