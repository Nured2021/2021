class UploadHandler:
    def __init__(self, capacity_manager, ai_sanitizer, file_processor, coordinator, workspace_transfer, sql_connector):
        self.capacity_manager = capacity_manager
        self.ai_sanitizer = ai_sanitizer
        self.file_processor = file_processor
        self.coordinator = coordinator
        self.workspace_transfer = workspace_transfer
        self.sql_connector = sql_connector
    def handle_upload(self, uploads):
        size_info = self.capacity_manager.analyze(uploads)
        print(size_info)
        cleaned = self.ai_sanitizer.sanitize(uploads)
        chunks = self.file_processor.process(cleaned)
        approved = self.coordinator.review(chunks)
        if approved:
            self.workspace_transfer.transfer(chunks)
            self.sql_connector.store_upload(chunks)
            print("[UPLOAD] Upload processed and stored.")
        else:
            print("[UPLOAD] Upload rejected by coordinator.")






