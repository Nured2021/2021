class BreakDetector:
    def is_ok(self, preview_status):
        # Simulate detection logic
        if preview_status in ['crash', 'blank', 'error', 'slow']:
            print(f"[PREVIEW] Issue detected: {preview_status}")
            return False
        return True






