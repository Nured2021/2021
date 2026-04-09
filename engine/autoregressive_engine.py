"""
AUTOREGRESSIVE ENGINE — Controlled Step-by-Step Generation
Generates outputs token-by-token or step-by-step, maintaining context and supporting long reasoning chains. Feeds intermediate outputs back into the system.
"""

class AutoregressiveEngine:
    def __init__(self, data_engine, transformers_engine):
        self.data_engine = data_engine
        self.transformers_engine = transformers_engine

    def generate(self, prompt, max_steps=10):
        context = self.data_engine.retrieve(prompt, context="working")
        plan = self.transformers_engine.think(prompt)
        steps = []
        current_input = prompt
        for i in range(max_steps):
            # Simulate step-by-step generation (token/segment)
            step = f"Step {i+1}: Generated for '{current_input}' with plan: {plan['objective']}"
            steps.append(step)
            # Feed intermediate output back into memory/context
            self.data_engine.working_memory.update(instruction=step)
            current_input = step  # Next step uses previous output
            # Optionally, allow Transformers Engine to review/refine at each step
            if hasattr(self.transformers_engine, 'review_step'):
                step = self.transformers_engine.review_step(step)
        # Final review by Transformers Engine
        reviewed = self.transformers_engine.reviewer.review(steps[-1])
        # Store final output in Data Engine
        self.data_engine.long_term_memory.add_output(reviewed)
        self.data_engine.vector_bridge.similarity_search(reviewed)
        self.data_engine.sql_bridge.save_record("autoregressive_output", {"result": reviewed})
        self.data_engine.preference_memory.set_preference("last_autoregressive_result", reviewed)
        return {
            "steps": steps,
            "final": reviewed
        }






