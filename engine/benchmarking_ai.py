class BenchmarkingAI:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def benchmark(self, system):
        result = f"Benchmarked: {system}"
        self.data_engine.long_term_memory.add_record(result)
        return result






