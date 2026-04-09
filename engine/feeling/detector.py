import re

class FeelingDetector:
    def detect(self, prompt):
        # Simple grammar/intent detection
        confidence = 1.0
        clarified_prompt = prompt
        intent = "build_request"
        if len(prompt.split()) < 3 or re.search(r"[^a-zA-Z0-9\s]", prompt):
            confidence = 0.5
            intent = "unclear_intent"
        if "fix" in prompt.lower():
            intent = "debug_request"
            clarified_prompt = "Fix broken code issue"
            confidence = 0.8
        elif "build" in prompt.lower():
            intent = "build_request"
            clarified_prompt = "Build the requested system"
            confidence = 0.9
        return {
            "intent": intent,
            "confidence": confidence,
            "clarified_prompt": clarified_prompt
        }






