class StateManagementCore:
    def __init__(self):
        self.state = {}
    def update(self, key, value):
        self.state[key] = value
    def get_state(self):
        return self.state






