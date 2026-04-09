class IntentInference:
    def infer_intent(self, user_input):
        # Simulate mapping rough input to tasks
        if "fix" in user_input:
            return ["debug", "stability"]
        elif "login" in user_input:
            return ["auth", "ui"]
        elif "theme" in user_input:
            return ["ui", "style"]
        else:
            return ["build"]






