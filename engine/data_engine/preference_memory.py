"""
PREFERENCE MEMORY — Remembers user preferences and style
Examples: theme, response length, fix-first, live preview, etc.
"""

class PreferenceMemory:
    def __init__(self):
        self.preferences = {}

    def set_preference(self, key, value):
        self.preferences[key] = value

    def get_preference(self, key):
        return self.preferences.get(key)

    def all_preferences(self):
        return self.preferences






