class AssetPipeline:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def manage(self, asset):
        result = f"Asset managed: {asset}"
        self.data_engine.long_term_memory.add_record(result)
        return result






