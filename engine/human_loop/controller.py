from .human_loop_brains import HumanLoopBrains


class HumanLoopController:
    def __init__(self):
        self.brains = HumanLoopBrains

    def activate(self, stage, context):
        resolved_stage = stage or "Human-in-the-loop"
        return {
            "active_brain": resolved_stage,
            "context": context,
            "status": "human_loop_engaged",
        }
