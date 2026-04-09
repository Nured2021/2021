class AuditLoggingCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def log(self, action):
        result = f"Audit log: {action}"
        self.data_engine.long_term_memory.add_record(result)
        return result






