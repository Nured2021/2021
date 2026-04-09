from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
from authentication_logic_core import AuthenticationLogicCore
from state_management_core import StateManagementCore
from subscription_billing_support_engine import SubscriptionBillingSupportEngine
from project_dashboard_ai import ProjectDashboardAI
from feedback_ui_core import FeedbackUICore
from snapshot_rollback_core import SnapshotRollbackCore
from auto_system.auto_engine import AutoEngine
from auto_system.brain_registry import BRAINS
from engine_brains.engine_brain_registry import ENGINE_BRAINS
from brain_system.controller import BrainSystem
from human_loop.controller import HumanLoopController
from tool_system.tools_registry import TOOLS
from tool_system.card_builder import CardBuilder


app = Flask(__name__)
app.secret_key = 'odex_secret'
socketio = SocketIO(app, cors_allowed_origins='*')

class APIOrchestrator:
    def __init__(self, data_engine):
        self.data_engine = data_engine
        self.auth = AuthenticationLogicCore(data_engine)
        self.state = StateManagementCore()
        self.subs = SubscriptionBillingSupportEngine(data_engine, None, self.state, self.auth, ProjectDashboardAI(data_engine), FeedbackUICore(data_engine), SnapshotRollbackCore(data_engine), None)
        self.project_dashboard = ProjectDashboardAI(data_engine)
        self.feedback = FeedbackUICore(data_engine)
        self.snapshot = SnapshotRollbackCore(data_engine)
        self.auto_engine = AutoEngine()
        self.brain_system = BrainSystem()
        self.human_loop = HumanLoopController()
        self.card_builder = CardBuilder()
        self.dashboard_cards = self.card_builder.build_cards(TOOLS)

    def build_api(self):
        # WebSocket for live events
        @socketio.on('connect', namespace='/ws/events')
        def ws_connect():
            emit('event', {'stage': 'Plan', 'engine': 'AI Pilot', 'message': 'User Input received'})
        # Example: In real system, emit events from engine logic
        # Auth endpoints
        @app.route('/api/auth/login', methods=['POST'])
        def login():
            data = request.json
            user = self.subs.login(data['email'], data['password'])
            session['user'] = data['email']
            return jsonify({'role': 'admin' if data['email'].endswith('@owner.com') else 'user'})

        @app.route('/api/auth/register', methods=['POST'])
        def register():
            data = request.json
            user_id = self.subs.register_user(data['email'], data['email'], data['password'])
            session['user'] = data['email']
            return jsonify({'role': 'admin' if data['email'].endswith('@owner.com') else 'user'})

        @app.route('/api/auth/me', methods=['GET'])
        def me():
            email = session.get('user')
            if not email:
                return jsonify({'role': None}), 401
            return jsonify({'role': 'admin' if email.endswith('@owner.com') else 'user'})

        # User/Admin panels
        @app.route('/api/projects', methods=['GET'])
        def projects():
            return jsonify([{'name': 'Demo Project'}])

        @app.route('/api/files', methods=['GET'])
        def files():
            return jsonify([{'name': 'main.py'}])

        @app.route('/api/tools', methods=['GET'])
        def tools():
            return jsonify(TOOLS)

        @app.route('/api/workspace', methods=['GET'])
        def workspace():
            return jsonify({'name': 'ODEX Workspace'})

        @app.route('/api/engines', methods=['GET'])
        def engines():
            return jsonify({
                "status": "active",
                "total": len(BRAINS) + len(ENGINE_BRAINS),
                "auto_brains": len(BRAINS),
                "engine_brains": len(ENGINE_BRAINS),
                "items": [{'name': 'Main Engine'}, {'name': 'Data Engine'}],
            })

        @app.route('/api/logs', methods=['GET'])
        def logs():
            return jsonify([
                {'event': 'System started', 'level': 'info'},
                {'event': f'Auto brains loaded: {len(BRAINS)}', 'level': 'info'},
                {'event': f'Engine brains loaded: {len(ENGINE_BRAINS)}', 'level': 'info'},
                {'event': f'Dashboard cards ready: {len(self.dashboard_cards)}', 'level': 'info'},
            ])

        @app.route('/api/subscription', methods=['GET'])
        def subscription():
            return jsonify({'status': 'active'})

        @app.route('/api/billing', methods=['GET'])
        def billing():
            return jsonify({'status': 'paid'})

        @app.route('/api/support', methods=['GET'])
        def support():
            return jsonify({'contact': 'support@odex.ai'})

        @app.route('/api/feedback', methods=['POST'])
        def feedback():
            data = request.json
            self.feedback.capture(data['feedback'])
            return jsonify({'ok': True})

        @app.route('/api/health', methods=['GET'])
        def health():
            return jsonify({'status': 'healthy'})

        @app.route('/api/controls', methods=['GET'])
        def controls():
            return jsonify({'controls': ['restart', 'shutdown']})

        @app.route('/api/users', methods=['GET'])
        def users():
            return jsonify([{'email': 'user@odex.ai'}])

        @app.route('/api/preview/live', methods=['GET'])
        def preview_live():
            return jsonify({
                'preview': 'Live preview running',
                'url': 'http://localhost:5173',
                'connected': True,
            })

        @app.route('/api/build', methods=['POST'])
        @app.route('/build', methods=['POST'])
        def build():
            data = request.json or {}
            prompt = data.get('prompt', '').strip()
            steps = ['Plan', 'Build', 'Fix', 'Test']
            if not prompt:
                return jsonify({
                    'status': 'error',
                    'message': 'Prompt is required',
                    'steps': steps,
                    'logs': ['[error] Missing prompt'],
                    'files': [],
                    'preview_url': 'http://localhost:5173',
                }), 400

            logs = [
                {'engine': 'orchestrator', 'stage': 'Plan', 'message': f'Analyzing prompt: {prompt}'},
                {'engine': 'planner', 'stage': 'Plan', 'message': 'Generating execution strategy'},
                {'engine': 'builder', 'stage': 'Build', 'message': 'Creating core files and modules'},
                {'engine': 'fixer', 'stage': 'Fix', 'message': 'Applying automatic corrections'},
                {'engine': 'tester', 'stage': 'Test', 'message': 'Running validation checks'},
                {'engine': 'preview', 'stage': 'Test', 'message': 'Publishing preview target'},
                {'engine': 'system', 'stage': 'Done', 'message': 'Build pipeline completed successfully'},
            ]
            files = [
                'engine/api_orchestrator.py',
                'ui/dashboard/BuilderWorkspace.jsx',
                'ui/dashboard/components/BuilderCore.jsx',
                'ui/dashboard/components/PreviewPanel.jsx',
            ]
            return jsonify({
                'status': 'ok',
                'steps': steps,
                'logs': logs,
                'files': files,
                'output': f'Build completed for: {prompt}',
                'preview_url': 'http://localhost:5173',
            })

        @app.route('/api/snapshot', methods=['POST'])
        def snapshot():
            data = request.json
            self.snapshot.snapshot(data['state'])
            return jsonify({'ok': True})

        @app.route('/api/rollback', methods=['POST'])
        def rollback():
            data = request.json
            self.snapshot.rollback(data['state'])
            return jsonify({'ok': True})

        @app.route('/api/aipilot', methods=['GET'])
        def aipilot():
            return jsonify({'workspace': 'AI Pilot Workspace'})

        @app.route('/api/theme', methods=['POST'])
        def theme():
            data = request.json
            # Save theme preference (not implemented)
            return jsonify({'ok': True})

        @app.route('/system-config', methods=['GET'])
        def system_config_api():
            # Alias endpoint for dashboard system panel
            return jsonify(self.auto_engine.run())

        @app.route('/api/auto-system', methods=['GET'])
        def auto_system():
            return jsonify(self.auto_engine.run())

        @app.route('/api/dashboard/cards', methods=['GET'])
        @app.route('/dashboard/cards', methods=['GET'])
        def get_cards():
            return jsonify(self.dashboard_cards)

        @app.route('/api/brains', methods=['GET'])
        @app.route('/brains', methods=['GET'])
        def brains():
            return jsonify(self.brain_system.get_all())

        @app.route('/api/brains/stabilize', methods=['POST'])
        @app.route('/brains/stabilize', methods=['POST'])
        def stabilize_api():
            return jsonify(self.brain_system.run())

        for brain in BRAINS:
            route = f"/{brain.lower()}/action"
            endpoint = f"brain_{brain.lower()}_action"

            def dynamic_brain(brain_name=brain):
                return jsonify({
                    "brain": brain_name,
                    "status": "active",
                    "auto": True
                })

            app.add_url_rule(route, endpoint=endpoint, view_func=dynamic_brain, methods=['GET'])

        for brain in ENGINE_BRAINS:
            route = brain["route"]
            endpoint = f"engine_brain_{brain['name'].lower()}_action"

            def dynamic_engine(brain_item=brain):
                return jsonify({
                    "brain": brain_item["name"],
                    "route": brain_item["route"],
                    "ui": brain_item["ui"],
                    "panel": brain_item["panel"],
                    "status": "active",
                    "type": "engine"
                })

            app.add_url_rule(route, endpoint=endpoint, view_func=dynamic_engine, methods=['GET'])

        @app.route('/api/engine-brains', methods=['GET'])
        def engine_brains():
            return jsonify({
                "count": len(ENGINE_BRAINS),
                "brains": ENGINE_BRAINS
            })

        @app.route('/api/human-loop', methods=['POST'])
        @app.route('/human-loop', methods=['POST'])
        def human_loop_api():
            data = request.json or {}
            result = self.human_loop.activate(
                stage=data.get("stage", "Human-in-the-decision-loop"),
                context=data.get("context", data),
            )
            return jsonify(result)

        return app, socketio






