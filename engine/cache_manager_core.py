class CacheManagerCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def cache(self, data):
        result = f"Cached: {data}"
        self.data_engine.long_term_memory.add_record(result)
        return result






