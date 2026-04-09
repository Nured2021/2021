# Tracks live UI state for ODEX

class LiveState:
    def __init__(self, stages):
        self.stages = stages
        self.current_stage = 0
        self.stage_status = ['pending'] * len(stages)
        self.logs = []
        self.spinner_frame = 0
        self.active_engine = None
        self.progress = 0
    def update_stage(self, idx, status):
        self.stage_status[idx] = status
        self.current_stage = idx
    def add_log(self, log):
        self.logs.append(log)
        if len(self.logs) > 10:
            self.logs = self.logs[-10:]
    def set_active_engine(self, engine):
        self.active_engine = engine
    def set_progress(self, progress):
        self.progress = progress






