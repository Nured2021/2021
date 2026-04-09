class FeelingInterpreter:
    def interpret(self, detection_result):
        # Map detection to pipeline action
        intent = detection_result.get("intent")
        if intent == "debug_request":
            return "debug"
        elif intent == "build_request":
            return "build"
        else:
            return "clarify"






