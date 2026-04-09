class BackupSyncCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def backup(self, data):
        self.data_engine.long_term_memory.add_record(f"Backup: {data}")
        return f"Backup complete for {data}"
    def sync(self, target):
        return f"Sync to {target} complete"






