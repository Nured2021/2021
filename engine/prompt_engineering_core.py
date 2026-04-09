class PromptEngineeringCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def refine(self, prompt):
        # Refine and optimize prompt
        refined = prompt + " [refined]"
        self.data_engine.working_memory.update(instruction=refined)
        return refined






