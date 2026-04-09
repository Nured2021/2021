class AIPilot:
    def __init__(self, main_engine):
        self.main_engine = main_engine
    def decide_path(self, request):
        # Master brain: decide which engines to activate
        return ["prompt_engineering", "memory", "transformers", "architecture_planner", "code_builder"]






