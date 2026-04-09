class ComplianceAI:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def check(self, system):
        result = f"Compliance checked for {system}"
        self.data_engine.long_term_memory.add_record(result)
        return result






