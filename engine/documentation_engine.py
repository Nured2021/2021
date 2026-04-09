class DocumentationEngine:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def generate_docs(self, system):
        doc = f"Documentation for {system}"
        self.data_engine.long_term_memory.add_record(doc)
        return doc






