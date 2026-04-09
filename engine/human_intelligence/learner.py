class HumanFeedbackLearner:
    def __init__(self):
        self.patterns = {}
    def learn(self, diffs):
        for key, ai_val, human_val in diffs:
            self.patterns[key] = human_val
    def get_preferences(self):
        return self.patterns






