class PreviewMonitor:
    def __init__(self, break_detector, recovery_manager):
        self.break_detector = break_detector
        self.recovery_manager = recovery_manager
        self.preview_ok = True
    def check(self, preview_status):
        if not self.break_detector.is_ok(preview_status):
            self.preview_ok = False
            self.recovery_manager.trigger_recovery(preview_status)
        else:
            self.preview_ok = True






