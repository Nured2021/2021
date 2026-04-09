class SnapshotRollbackCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def snapshot(self, state):
        self.data_engine.long_term_memory.add_record(f"Snapshot: {state}")
        return f"Snapshot saved: {state}"
    def rollback(self, state):
        return f"Rolled back to: {state}"






