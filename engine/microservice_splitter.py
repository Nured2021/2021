class MicroserviceSplitter:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def split(self, system):
        result = f"Microservices created for {system}"
        self.data_engine.long_term_memory.add_record(result)
        return result






