class FeedbackUICore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def capture(self, feedback):
        self.data_engine.long_term_memory.add_record(f"Feedback: {feedback}")
        return f"Feedback captured: {feedback}"






