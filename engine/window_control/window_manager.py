class WindowManager:
    def __init__(self, layout_engine, screen_detector):
        self.layout_engine = layout_engine
        self.screen_detector = screen_detector
        self.windows = {}
    def suggest_new_window(self, reason):
        print(f"[WINDOW] {reason} Open new window for better workspace? (Yes / No)")
        resp = input().strip().lower()
        if resp == 'yes':
            self.open_window('extra')
    def open_window(self, window_type):
        self.windows[window_type] = True
        print(f"[WINDOW] Opened {window_type} window.")
    def close_window(self, window_type):
        if window_type in self.windows:
            del self.windows[window_type]
            print(f"[WINDOW] Closed {window_type} window.")
    def organize(self):
        screens = self.screen_detector.detect_screens()
        self.layout_engine.arrange(screens, self.windows)






