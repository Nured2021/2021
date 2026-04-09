class LearnGoCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def improve(self, feedback):
        improved = f"Learned from {feedback}"
        self.data_engine.long_term_memory.add_record(improved)
        return improved






