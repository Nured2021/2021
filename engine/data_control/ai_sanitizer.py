class AISanitizer:
    def sanitize(self, uploads):
        # Simulate cleaning, error scan, normalization
        cleaned = []
        for u in uploads:
            cleaned.append(str(u).replace('\r','').replace('\t','    '))
        print("[SANITIZER] Data cleaned and normalized.")
        return cleaned






