class AuthenticationLogicCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def authenticate(self, user):
        return f"Authenticated: {user}"
    def authorize(self, user, role):
        return f"Authorized: {user} as {role}"






