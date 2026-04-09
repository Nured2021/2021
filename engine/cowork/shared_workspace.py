class SharedWorkspace:
    def __init__(self):
        self.human_panel = []
        self.ai_panel = []
        self.task_board = []
        self.file_changes = []
        self.approval_bar = []
    def update_panels(self, human_action, ai_action):
        self.human_panel.append(human_action)
        self.ai_panel.append(ai_action)
        self.task_board.append(f"Human: {human_action} | AI: {ai_action}")
    def add_file_change(self, file, change):
        self.file_changes.append((file, change))
    def add_approval(self, action):
        self.approval_bar.append(action)
    def get_state(self):
        return {
            'human_panel': self.human_panel[-5:],
            'ai_panel': self.ai_panel[-5:],
            'task_board': self.task_board[-10:],
            'file_changes': self.file_changes[-10:],
            'approval_bar': self.approval_bar[-5:]
        }






