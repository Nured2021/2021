class UserInputEngine:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def receive(self, user_input):
        # Normalize and store input
        norm = user_input.strip()
        self.data_engine.working_memory.update(prompt=norm)
        return norm






