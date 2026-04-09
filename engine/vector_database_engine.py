class VectorDatabaseEngine:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def embed(self, data):
        result = f"Embedded: {data}"
        self.data_engine.vector_bridge.similarity_search(result)
        return result






