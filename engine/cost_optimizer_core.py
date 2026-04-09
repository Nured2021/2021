class CostOptimizerCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def optimize(self, system):
        result = f"Cost optimized for {system}"
        self.data_engine.long_term_memory.add_record(result)
        return result






