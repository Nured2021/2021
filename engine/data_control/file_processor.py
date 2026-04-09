class FileProcessor:
    def process(self, cleaned_uploads):
        # Simulate chunking and extraction
        chunks = []
        for c in cleaned_uploads:
            chunks.append({'content': c[:100], 'length': len(c)})
        print(f"[PROCESSOR] Processed {len(chunks)} chunks.")
        return chunks






