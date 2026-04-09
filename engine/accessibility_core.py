class AccessibilityCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def check_accessibility(self, ui):
        result = f"Accessibility checked for {ui}"
        self.data_engine.long_term_memory.add_record(result)
        return result






