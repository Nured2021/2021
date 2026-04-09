"""
LONG-TERM MEMORY — Persistent project history
Stores past builds, fixes, architecture choices, preferences, outputs, learned patterns.
"""

class LongTermMemory:
    def __init__(self):
        self.project_history = []
        self.user_preferences = {}
        self.saved_outputs = []
        self.learned_patterns = []

    def add_record(self, record):
        self.project_history.append(record)

    def add_preference(self, key, value):
        self.user_preferences[key] = value

    def add_output(self, output):
        self.saved_outputs.append(output)

    def add_pattern(self, pattern):
        self.learned_patterns.append(pattern)

    def get_history(self):
        return self.project_history

    def get_preferences(self):
        return self.user_preferences

    def get_outputs(self):
        return self.saved_outputs

    def get_patterns(self):
        return self.learned_patterns






