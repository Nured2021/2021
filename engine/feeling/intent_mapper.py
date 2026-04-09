class IntentMapper:
    def map_intent(self, prompt):
        # Simple mapping for demo
        if "fix" in prompt.lower():
            return "debug"
        elif "build" in prompt.lower():
            return "build"
        else:
            return "clarify"






