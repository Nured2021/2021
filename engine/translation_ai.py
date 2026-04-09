class TranslationAI:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def translate(self, text, lang):
        result = f"Translated to {lang}: {text}"
        self.data_engine.long_term_memory.add_record(result)
        return result






