class AnalyticsBICore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
        self.metrics = []
    def collect(self, metric):
        self.metrics.append(metric)
        self.data_engine.long_term_memory.add_record(metric)
        return metric






