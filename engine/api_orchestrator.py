from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
from authentication_logic_core import AuthenticationLogicCore
from state_management_core import StateManagementCore
from subscription_billing_support_engine import SubscriptionBillingSupportEngine
from project_dashboard_ai import ProjectDashboardAI
from feedback_ui_core import FeedbackUICore
from snapshot_rollback_core import SnapshotRollbackCore


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
            return jsonify([{'name': 'Tool 1'}])

        @app.route('/api/workspace', methods=['GET'])
        def workspace():
            return jsonify({'name': 'ODEX Workspace'})

        @app.route('/api/engines', methods=['GET'])
        def engines():
            return jsonify([{'name': 'Main Engine'}, {'name': 'Data Engine'}])

        @app.route('/api/logs', methods=['GET'])
        def logs():
            return jsonify([{'event': 'System started'}])

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
            return jsonify({'preview': 'Live preview running'})

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

        return app, socketio






