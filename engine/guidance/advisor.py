class GuidanceAdvisor:
    def advise(self, intent, prompt):
        if intent == "debug":
            return "Got it — looks like you want to fix broken code. I’m starting debug stage now. I will scan and repair the system."
        elif intent == "build":
            return "Understood — building your requested system now."
        else:
            return "Could you clarify your request?"






