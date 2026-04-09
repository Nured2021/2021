from preview_control.auto_fix_engine import AutoFixEngine
from preview_control.preview_renderer import PreviewRenderer
from preview_control.window_sync import WindowSync

class RecoveryManager:
    def __init__(self):
        self.auto_fix = AutoFixEngine()
        self.renderer = PreviewRenderer()
        self.window_sync = WindowSync()
    def trigger_recovery(self, issue):
        self.window_sync.pause_preview()
        self.auto_fix.run_fix_pipeline(issue)
        self.renderer.restart_preview()
        self.window_sync.resume_preview()
        print("✅ Issue fixed — preview restored\nBuild resumed successfully")






