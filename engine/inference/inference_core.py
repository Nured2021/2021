class InferenceCore:
    def __init__(self, reasoning_chain, intent_inference, context_predictor, solution_ranker):
        self.reasoning_chain = reasoning_chain
        self.intent_inference = intent_inference
        self.context_predictor = context_predictor
        self.solution_ranker = solution_ranker
    def infer(self, user_input, feeling_state, memory, workspace_state, queue):
        reasoning = self.reasoning_chain.reason(user_input, feeling_state, memory, workspace_state, queue)
        intent = self.intent_inference.infer_intent(user_input)
        context = self.context_predictor.predict(memory, workspace_state, queue)
        ranked = self.solution_ranker.rank(reasoning, intent, context)
        return ranked






