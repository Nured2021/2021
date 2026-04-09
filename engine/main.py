from main_engine import MainEngine
from api_orchestrator import APIOrchestrator


def main():
    engine = MainEngine()
    api = APIOrchestrator(engine.data_engine)
    app, socketio = api.build_api()
    # Serve UI static files from ../ui/public
    import os
    from flask import send_from_directory
    ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ui/public'))

    @app.route('/')
    def index():
        return send_from_directory(ui_path, 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory(ui_path, path)

    socketio.run(app, host='0.0.0.0', port=8080, debug=True)

if __name__ == "__main__":
    main()






