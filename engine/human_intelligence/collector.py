class HumanFeedbackCollector:
    def __init__(self):
        self.edits = []
        self.selections = []
        self.overrides = []

    def capture_edit(self, edit):
        self.edits.append(edit)

    def capture_selection(self, selection):
        self.selections.append(selection)

    def capture_override(self, override):
        self.overrides.append(override)

    def get_feedback(self):
        return {
            'edits': self.edits,
            'selections': self.selections,
            'overrides': self.overrides
        }






