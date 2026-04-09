class CapacityManager:
    def analyze(self, uploads):
        # Simulate size/page/complexity detection
        size = sum(len(str(u)) for u in uploads)
        pages = len(uploads)
        msg = f"Large upload detected. {pages} files, {size} bytes. Processing now."
        return msg






