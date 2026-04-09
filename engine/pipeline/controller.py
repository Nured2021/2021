from pipeline.stages import PipelineStages
from orchestrator import Orchestrator

from human_intelligence.injector import HumanPreferenceInjector
from human_intelligence.learner import HumanFeedbackLearner
from human_intelligence.collector import HumanFeedbackCollector
from human_intelligence.analyzer import HumanFeedbackAnalyzer

from ui.live_state import LiveState
from ui.renderer import UIRenderer

class PipelineController:
    def __init__(self):
        self.stages = PipelineStages()
        self.orchestrator = Orchestrator()
        self.learner = HumanFeedbackLearner()
        self.injector = HumanPreferenceInjector()
        self.collector = HumanFeedbackCollector()
        self.analyzer = HumanFeedbackAnalyzer()
        self.ui_state = LiveState(["PLAN", "BUILD", "FIX", "TEST", "DEPLOY"])
        self.ui = UIRenderer(self.ui_state)

    def run_pipeline(self, user_prompt, intent=None):
        context = {'prompt': user_prompt}
        outputs = []
        stages = self.stages.get_stages()
        preferences = self.learner.get_preferences()
        context = self.injector.inject(context, preferences)
        interrupted = False
        self.ui_state.logs.clear()
        for idx, stage in enumerate(stages):
            # UI: update stage
            self.ui_state.update_stage(idx, 'active')
            self.ui_state.add_log(f"[AI BRAIN] → {stage.__name__.replace('_stage','').upper()} stage running...")
            self.ui.render()
            # Interrupt logic
            if intent == "debug_request" and stage.__name__ == 'debug_stage':
                result = stage(context, self.orchestrator)
                outputs.append("[INTERRUPT] Debug stage forced by user.")
                outputs.append(result)
                self.ui_state.update_stage(idx, 'done')
                self.ui_state.add_log("[DEBUG] → Debug complete.")
                self.ui.render()
                interrupted = True
                break
            result = stage(context, self.orchestrator)
            outputs.append(result)
            self.ui_state.update_stage(idx, 'done')
            self.ui_state.add_log(f"[AI BRAIN] → {stage.__name__.replace('_stage','').upper()} complete.")
            self.ui.render()
            if stage.__name__ == 'build_stage':
                ai_output = {'structure': 'default'}
                human_edit = {'structure': 'user_modified'}
                diffs = self.analyzer.compare_outputs(ai_output, human_edit)
                self.learner.learn(diffs)
        if interrupted:
            for stage in stages[idx+1:]:
                self.ui_state.update_stage(idx, 'active')
                self.ui_state.add_log(f"[AI BRAIN] → {stage.__name__.replace('_stage','').upper()} stage running...")
                self.ui.render()
                result = stage(context, self.orchestrator)
                outputs.append(result)
                self.ui_state.update_stage(idx, 'done')
                self.ui_state.add_log(f"[AI BRAIN] → {stage.__name__.replace('_stage','').upper()} complete.")
                self.ui.render()
        proof = {
            "status": "DONE",
            "message": "System built successfully" if not intent or intent == "build_request" else "Debug complete",
            "files_created": ["output_project/"],
            "preview_url": "/output",
            "logs": outputs
        }
        self.ui_state.add_log("[SYSTEM] → Pipeline complete.")
        self.ui.render()
        return proof






