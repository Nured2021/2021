class Context:
    def __init__(self, prompt):
        self.prompt = prompt
        self.vars = {}
    def set(self, key, value):
        self.vars[key] = value
    def get(self, key, default=None):
        return self.vars.get(key, default)






