"""
Conversational Intelligence Engine — Main Front-Facing AI Brain for ODEX
Acts as the live, human-facing control and explanation layer. Feeds all other engines and keeps the user connected to the system at all times.
"""

class ConversationalIntelligenceEngine:
    def __init__(self, main_engine, data_engine, event_system, state_management, ai_pilot, feedback_ui_core, collaboration_engine, project_dashboard_ai):
        self.main_engine = main_engine
        self.data_engine = data_engine
        self.event_system = event_system
        self.state_management = state_management
        self.ai_pilot = ai_pilot
        self.feedback_ui_core = feedback_ui_core
        self.collaboration_engine = collaboration_engine
        self.project_dashboard_ai = project_dashboard_ai
        # Sub-engines
        self.user_input_engine = main_engine.user_input_engine
        self.collaboration_engine = main_engine.collaboration_engine
        self.prompt_engineering_core = main_engine.prompt_engineering_core
        self.memory_pipeline_core = main_engine.memory_pipeline_core
        self.vector_database_engine = main_engine.vector_database_engine
        self.learn_go_core = main_engine.learn_go_core
        self.response_engine = ResponseEngine(self)
        self.guidance_engine = GuidanceEngine(self)
        self.confidence_engine = ConfidenceEngine(self)
        self.file_intake_engine = FileIntakeEngine(self)
        self.progress_engine = ProgressEngine(self)
        self.human_loop_engine = HumanLoopEngine(self)
        self.context_engine = ContextEngine(self)

    def handle_user_input(self, input_data, input_type="text", user_id=None):
        # Accepts text, voice, file, or edit, per user
        # Step 1: Capture input per user
        if input_type == "file":
            raw_input = self.user_input_engine.capture(input_data, input_type="file", user_id=user_id)
        else:
            raw_input = self.user_input_engine.capture(input_data, user_id=user_id)

        # Step 2: Collaboration Engine merges/syncs/organizes input for multi-user
        collab_input = self.collaboration_engine.collaborate(user_id or "user", raw_input)

        # Step 3: Prompt Engineering Core translates
        engineered = self.prompt_engineering_core.engineer(collab_input)
        # Step 4: Memory Pipeline Core adds context
        memory_context = self.memory_pipeline_core.retrieve_context(engineered)
        # Step 5: Learn & Go Core applies user preferences
        personalized_prompt = self.learn_go_core.apply_preferences(engineered, memory_context, user_id=user_id)
        self.context_engine.update_context(raw_input)
        # Step 6: AI Pilot makes all decisions and routes tasks
        ai_decision = self.ai_pilot.decide(personalized_prompt, user_id=user_id)
        self.event_system.trigger(f"User input: {raw_input}")
        self.progress_engine.show("Processing input...")
        if ai_decision.get("proceed", True):
            answer = self.learn_go_core.personalize_response(personalized_prompt, self.response_engine, user_id=user_id)
            self.confidence_engine.show_confidence(answer)
            if input_type == "file":
                self.memory_pipeline_core.store_file(input_data, user_id=user_id)
            self.memory_pipeline_core.store_qa(raw_input, answer, user_id=user_id)
            self.learn_go_core.update_preferences(raw_input, answer, user_id=user_id)
            self.response_engine.respond(answer)
            return answer
        else:
            self.response_engine.respond(ai_decision.get("message", "Action not approved."))
            return ai_decision.get("message", "Action not approved.")

    def update_user(self, message):
        self.response_engine.respond(message)
        self.progress_engine.show(message)

    def explain_status(self):
        status = self.project_dashboard_ai.show()
        self.guidance_engine.explain(status)

    def ask_for_approval(self, question):
        return self.human_loop_engine.ask(question)

    def present_result(self, result):
        self.response_engine.respond(result)
        self.progress_engine.show("Build complete.")

# --- Sub-Engines ---
class ResponseEngine:
    def __init__(self, parent): self.parent = parent
    def respond(self, message):
        # Simulate plain language response
        print(f"[AI] {message}")
        return message

class GuidanceEngine:
    def __init__(self, parent): self.parent = parent
    def explain(self, status):
        print(f"[GUIDE] {status}")

class ConfidenceEngine:
    def __init__(self, parent): self.parent = parent
    def show_confidence(self, answer):
        # Simulate confidence reporting
        print(f"[CONFIDENCE] Answer confidence: high")

class FileIntakeEngine:
    def __init__(self, parent): self.parent = parent
    def process_file(self, file_data):
        # Simulate file intake and routing
        return f"File '{file_data}' received and routed."

class ProgressEngine:
    def __init__(self, parent): self.parent = parent
    def show(self, progress):
        print(f"[PROGRESS] {progress}")

class HumanLoopEngine:
    def __init__(self, parent): self.parent = parent
    def ask(self, question):
        print(f"[HUMAN APPROVAL NEEDED] {question}")
        return input(f"{question} (y/n): ")

class ContextEngine:
    def __init__(self, parent): self.parent = parent
    def update_context(self, prompt):
        # Simulate context update
        self.parent.data_engine.receive_data(prompt, source="conversation")
        print(f"[CONTEXT] Updated with: {prompt}")






