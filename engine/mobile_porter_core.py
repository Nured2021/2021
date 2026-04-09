class MobilePorterCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def port(self, system):
        result = f"Ported to mobile: {system}"
        self.data_engine.long_term_memory.add_record(result)
        return result






