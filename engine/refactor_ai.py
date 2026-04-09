class RefactorAI:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def refactor(self, code):
        result = f"Code refactored: {code}"
        self.data_engine.long_term_memory.add_record(result)
        return result






