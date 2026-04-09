class RefiningCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def refine(self, output):
        result = f"Refined: {output}"
        self.data_engine.long_term_memory.add_output(result)
        return result






