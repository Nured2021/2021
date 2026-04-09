class MemoryPipelineCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def connect(self, data):
        self.data_engine.receive_data(data, source="memory_pipeline")
        return f"Memory pipeline processed {data}"






