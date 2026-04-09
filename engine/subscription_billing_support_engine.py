"""
Subscription, Billing, User Control, and Support Engine — Internal Business Operations Core
Handles all business, account, billing, and support logic for ODEX. Hidden from public, available only in owner/admin workspace.
"""

class SubscriptionBillingSupportEngine:
    def __init__(self, data_engine, event_system, state_management, auth_logic_core, project_dashboard_ai, feedback_ui_core, snapshot_rollback_core, finalization_engine):
        self.data_engine = data_engine
        self.event_system = event_system
        self.state_management = state_management
        self.auth_logic_core = auth_logic_core
        self.project_dashboard_ai = project_dashboard_ai
        self.feedback_ui_core = feedback_ui_core
        self.snapshot_rollback_core = snapshot_rollback_core
        self.finalization_engine = finalization_engine
        self.users = {}
        self.projects = {}
        self.cases = []
        self.ai_team = self._init_ai_team()
        self.admin_workspace = {}
        self.owner_panel = {}

    def _init_ai_team(self):
        return {
            "leader": LeaderAI(self),
            "coordinator": CoordinatorAI(self),
            "billing": BillingAI(self),
            "policy": PolicyAI(self),
            "support": SupportAI(self),
            "sales": SalesAI(self),
            "recovery": RecoveryAI(self),
            "communication": CommunicationAI(self)
        }

    # --- User Registration, Login, Account Control ---
    def register_user(self, name, email, password):
        user_id = self.auth_logic_core.authenticate(email)
        self.users[email] = {
            "name": name,
            "email": email,
            "password": password,
            "plan": "free",
            "credits": 100,
            "usage": 0,
            "status": "active",
            "history": [],
            "projects": [],
            "invoices": [],
            "receipts": [],
            "warnings": [],
            "support": []
        }
        self.event_system.trigger(f"User registered: {email}")
        self.state_management.update(email, "active")
        return user_id

    def login(self, email, password):
        user = self.users.get(email)
        if user and user["password"] == password:
            self.state_management.update(email, "active")
            return True
        return False

    def update_account(self, email, **kwargs):
        user = self.users.get(email)
        if user:
            user.update(kwargs)
            self.event_system.trigger(f"Account updated: {email}")
            return True
        return False

    # --- Subscription, Credits, Usage, Billing ---
    def subscribe(self, email, plan):
        user = self.users.get(email)
        if user:
            user["plan"] = plan
            user["credits"] = self._plan_credits(plan)
            self.event_system.trigger(f"Subscription changed: {email} → {plan}")
            return True
        return False

    def _plan_credits(self, plan):
        return {"free": 100, "pro": 1000, "enterprise": 10000}.get(plan, 100)

    def use_credits(self, email, amount):
        user = self.users.get(email)
        if user and user["credits"] >= amount:
            user["credits"] -= amount
            user["usage"] += amount
            self.state_management.update(email, f"used {user['usage']}")
            if user["credits"] < 10:
                self.event_system.trigger(f"Low credits warning: {email}")
            return True
        return False

    def charge(self, email, amount, description):
        user = self.users.get(email)
        if user:
            invoice = {"amount": amount, "desc": description, "status": "charged"}
            user["invoices"].append(invoice)
            self.finalization_engine.finalize(invoice)
            self.event_system.trigger(f"Charged: {email} {amount}")
            return True
        return False

    def record_payment(self, email, amount, method):
        user = self.users.get(email)
        if user:
            receipt = {"amount": amount, "method": method, "status": "paid"}
            user["receipts"].append(receipt)
            self.finalization_engine.finalize(receipt)
            return True
        return False

    # --- Policy, Abuse, Blocking, Warnings ---
    def warn_user(self, email, reason):
        user = self.users.get(email)
        if user:
            user["warnings"].append(reason)
            self.event_system.trigger(f"Warning: {email} {reason}")
            return True
        return False

    def block_user(self, email, reason):
        user = self.users.get(email)
        if user:
            user["status"] = "blocked"
            self.state_management.update(email, "blocked")
            self.event_system.trigger(f"Blocked: {email} {reason}")
            return True
        return False

    # --- Project Ownership, Usage, Deletion, Recovery ---
    def link_project(self, email, project_name):
        user = self.users.get(email)
        if user:
            user["projects"].append(project_name)
            self.projects[project_name] = email
            return True
        return False

    def delete_project(self, email, project_name):
        user = self.users.get(email)
        if user and project_name in user["projects"]:
            user["projects"].remove(project_name)
            self.snapshot_rollback_core.snapshot(f"Before delete: {project_name}")
            self.event_system.trigger(f"Project deleted: {project_name}")
            return True
        return False

    def recover_project(self, email, project_name):
        user = self.users.get(email)
        if user:
            self.snapshot_rollback_core.rollback(f"Recover: {project_name}")
            self.event_system.trigger(f"Project recovered: {project_name}")
            return True
        return False

    # --- Cancellation, Deletion, Refund, Support ---
    def cancel_subscription(self, email):
        user = self.users.get(email)
        if user:
            user["plan"] = "cancelled"
            self.event_system.trigger(f"Subscription cancelled: {email}")
            return True
        return False

    def delete_account(self, email):
        if email in self.users:
            self.snapshot_rollback_core.snapshot(f"Before delete: {email}")
            del self.users[email]
            self.event_system.trigger(f"Account deleted: {email}")
            return True
        return False

    def refund(self, email, amount):
        user = self.users.get(email)
        if user:
            case = {"type": "refund", "email": email, "amount": amount}
            self.cases.append(case)
            self.event_system.trigger(f"Refund requested: {email} {amount}")
            return True
        return False

    def support_ticket(self, email, issue, project_name=None):
        user = self.users.get(email)
        if user:
            ticket = {"email": email, "issue": issue, "project": project_name, "status": "open"}
            user["support"].append(ticket)
            self.cases.append(ticket)
            self.feedback_ui_core.capture(issue)
            self.event_system.trigger(f"Support ticket: {email} {issue}")
            return True
        return False

    # --- Admin/Owner Workspace, Escalation, Email ---
    def escalate_to_owner(self, email, issue, project_name=None):
        user = self.users.get(email)
        if user:
            case = {
                "email": email,
                "name": user["name"],
                "issue": issue,
                "project": project_name,
                "status": user["status"],
                "summary": f"{issue} for {project_name}",
                "history": user["history"]
            }
            self.admin_workspace[email] = case
            self._send_email_to_owner(case)
            return True
        return False

    def _send_email_to_owner(self, case):
        # Simulate email sending
        self.ai_team["communication"].prepare_email(case)
        self.event_system.trigger(f"Escalated to owner: {case['email']}")

    # --- User/Owner Panels ---
    def get_user_panel(self, email):
        user = self.users.get(email)
        if user:
            return {
                "plan": user["plan"],
                "credits": user["credits"],
                "usage": user["usage"],
                "invoices": user["invoices"],
                "receipts": user["receipts"],
                "support": user["support"]
            }
        return None

    def get_owner_panel(self):
        return self.admin_workspace

# --- AI Team Classes (Internal) ---
class LeaderAI:
    def __init__(self, engine): self.engine = engine
class CoordinatorAI:
    def __init__(self, engine): self.engine = engine
class BillingAI:
    def __init__(self, engine): self.engine = engine
class PolicyAI:
    def __init__(self, engine): self.engine = engine
class SupportAI:
    def __init__(self, engine): self.engine = engine
class SalesAI:
    def __init__(self, engine): self.engine = engine
class RecoveryAI:
    def __init__(self, engine): self.engine = engine
class CommunicationAI:
    def __init__(self, engine): self.engine = engine
    def prepare_email(self, case):
        # Simulate email preparation
        return f"Email prepared for {case['email']} re: {case['issue']}"






