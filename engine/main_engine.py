from refining_core import RefiningCore
from vector_database_engine import VectorDatabaseEngine
from authentication_logic_core import AuthenticationLogicCore
from asset_pipeline import AssetPipeline
from collaboration_engine import CollaborationEngine as ODEXCollaborationEngine
from project_dashboard_ai import ProjectDashboardAI
from search_engine_core import SearchEngineCore
from feedback_ui_core import FeedbackUICore
from snapshot_rollback_core import SnapshotRollbackCore
from finalization_engine import FinalizationEngine
from backup_sync_core import BackupSyncCore
from failsafe_sentry_core import FailsafeSentryCore
from toolchain_core import ToolchainCore
from update_patch_core import UpdatePatchCore
from documentation_engine import DocumentationEngine
from accessibility_core import AccessibilityCore
from seo_performance_core import SEOPerformanceCore
from mobile_porter_core import MobilePorterCore
from compliance_ai import ComplianceAI
from conflict_resolver import ConflictResolver
from code_reviewer_ai import CodeReviewerAI
from refactor_ai import RefactorAI
from microservice_splitter import MicroserviceSplitter
from cache_manager_core import CacheManagerCore
from audit_logging_core import AuditLoggingCore
from resource_monitor_core import ResourceMonitorCore
from cost_optimizer_core import CostOptimizerCore
from translation_ai import TranslationAI
from benchmarking_ai import BenchmarkingAI
from health_check_ai import HealthCheckAI
from user_input_engine import UserInputEngine
from ai_pilot import AIPilot
from prompt_engineering_core import PromptEngineeringCore
from event_system_core import EventSystemCore
from state_management_core import StateManagementCore
from architecture_planner import ArchitecturePlanner
from code_builder_engine import CodeBuilderEngine
from debugger_fixer import DebuggerFixer
from unit_testing_core import UnitTestingCore
from integration_testing_core import IntegrationTestingCore
from uiux_design_engine import UIUXDesignEngine
from database_schema_core import DatabaseSchemaCore
from api_orchestrator import APIOrchestrator
from security_hardening_core import SecurityHardeningCore
from cicd_deployment_core import CICDDeploymentCore
from memory_pipeline_core import MemoryPipelineCore
from learn_go_core import LearnGoCore
from task_queue_core import TaskQueueCore
from plugin_system_core import PluginSystemCore
from analytics_bi_core import AnalyticsBICore
from agentic_engine import AgenticEngine
from feeling.detector import FeelingDetector
from guidance.advisor import GuidanceAdvisor
from guidance.responder import GuidanceResponder
from storage.chat_store import ChatStore
from pipeline.controller import PipelineController
from human_intelligence.collector import HumanFeedbackCollector
from human_intelligence.analyzer import HumanFeedbackAnalyzer
from human_intelligence.learner import HumanFeedbackLearner
from human_intelligence.injector import HumanPreferenceInjector
from cowork.collaboration_engine import CollaborationEngine
from cowork.shared_workspace import SharedWorkspace
from cowork.human_ai_bridge import HumanAIBridge
from cowork.intent_sync import IntentSync
from cowork.trust_layer import TrustLayer
from cowork.live_dialogue import LiveDialogue
from window_control.window_manager import WindowManager
from window_control.layout_engine import LayoutEngine
from window_control.screen_detector import ScreenDetector
from window_control.focus_engine import FocusEngine
from window_control.qc_validator import QCValidator
from brains.leader_brain import LeaderBrain
from brains.coordinator_brain import CoordinatorBrain
from brains.worker_brains import WorkerBrains
from brains.brain_dialogue import BrainDialogue
from data_control.upload_handler import UploadHandler
from data_control.capacity_manager import CapacityManager
from data_control.ai_sanitizer import AISanitizer
from data_control.file_processor import FileProcessor
from data_control.workspace_transfer import WorkspaceTransfer
from data_control.sql_connector import SQLConnector
from preview_control.preview_monitor import PreviewMonitor
from preview_control.break_detector import BreakDetector
from preview_control.recovery_manager import RecoveryManager
from vibe.leader_ai import LeaderAI as VibeLeaderAI
from vibe.coordinator_ai import VibeCoordinatorAI
from vibe.architect_ai import ArchitectAI
from vibe.builder_ai import BuilderAI
from vibe.debugger_ai import DebuggerAI
from vibe.reviewer_ai import ReviewerAI
from vibe.discussion_engine import DiscussionEngine
from vibe.decision_engine import DecisionEngine
from inference.inference_core import InferenceCore
from inference.reasoning_chain import ReasoningChain
from data_engine.data_core import DataCore
from transformers_engine import TransformersEngine
from autoregressive_engine import AutoregressiveEngine
from inference_engine import ODEXInferenceEngine
from training_engine import TrainingEngine
from execution_engine import ExecutionEngine
from planning_engine import PlanningEngine
from control_engine import ControlEngine
from communication_engine import CommunicationEngine
from observation_engine import ObservationEngine
from adaptation_engine import AdaptationEngine
from safety_engine import SafetyEngine
from inference.intent_inference import IntentInference
from inference.context_predictor import ContextPredictor
from inference.solution_ranker import SolutionRanker

class MainEngine:
    def __init__(self):
        # ...existing code initializing dependencies...
        # SYSTEM MECHANICS / HAMMERS / BUILDER / FIXER / RISK HUNTER LAYER (HIDDEN, BACKGROUND)
        from system_mechanics_layer import SystemMechanicsLayer
        self.system_mechanics_layer = SystemMechanicsLayer(
            main_engine=self,
            data_engine=self.data_engine,
            event_system=self.event_system_core,
            state_management=self.state_management_core,
            failsafe_sentry_core=self.failsafe_sentry_core,
            debugger_fixer=self.debugger_fixer,
            health_check_ai=self.health_check_ai,
            resource_monitor_core=self.resource_monitor_core,
            audit_logging_core=self.audit_logging_core,
            snapshot_rollback_core=self.snapshot_rollback_core,
            agentic_engine=self.agentic_engine,
            transformers_engine=self.transformers_engine
        )

    def get_interface_mode(self, email):
        # Use Authentication Logic Core to detect role
        user_role = self.authentication_logic_core.authorize(email, None)
        if user_role == "owner":
            self.state_management_core.update(email, "owner_mode")
            self.event_system_core.trigger(f"Interface mode: OWNER for {email}")
            return "owner"
        else:
            self.state_management_core.update(email, "user_mode")
            self.event_system_core.trigger(f"Interface mode: USER for {email}")
            return "user"

    def get_visible_components(self, email):
        mode = self.get_interface_mode(email)
        if mode == "owner":
            return {
                "engines": "all",
                "main_engine": True,
                "data_engine": True,
                "event_system": True,
                "state_management": True,
                "task_queue": True,
                "ai_activity": True,
                "token_usage": True,
                "user_accounts": True,
                "projects": True,
                "subscription_billing_support": True,
                "logs": True,
                "errors": True,
                "recovery": True,
                "security": True,
                "admin_tools": True,
                "override": True,
                "private_workspace": True
            }
        else:
            return {
                "prompt_box": True,
                "live_preview": True,
                "files_basic": True,
                "progress": True,
                "feedback_popups": True,
                "user_projects": True,
                "usage_panel": True,
                "billing_panel": True,
                "internal_engines": False,
                "system_structure": False,
                "admin_tools": False,
                "backend": False,
                "private_workspace": False
            }
        # MAIN CONVERSATIONAL INTELLIGENCE ENGINE (FRONT-FACING AI)
        from conversational_intelligence_engine import ConversationalIntelligenceEngine
        self.conversational_intelligence_engine = ConversationalIntelligenceEngine(
            main_engine=self,
            data_engine=self.data_engine,
            event_system=self.event_system_core,
            state_management=self.state_management_core,
            ai_pilot=self.ai_pilot,
            feedback_ui_core=self.feedback_ui_core,
            collaboration_engine=self.collaboration_engine,
            project_dashboard_ai=self.project_dashboard_ai
        )
        # FINAL SYSTEM CORES (C-41 to C-50)
        self.refining_core = RefiningCore(self.data_engine)
        self.vector_database_engine = VectorDatabaseEngine(self.data_engine)
        self.authentication_logic_core = AuthenticationLogicCore(self.data_engine)
        self.asset_pipeline = AssetPipeline(self.data_engine)
        self.collaboration_engine = ODEXCollaborationEngine(self.data_engine)
        self.project_dashboard_ai = ProjectDashboardAI(self.data_engine)
        self.search_engine_core = SearchEngineCore(self.data_engine)
        self.feedback_ui_core = FeedbackUICore(self.data_engine)
        self.snapshot_rollback_core = SnapshotRollbackCore(self.data_engine)
        self.finalization_engine = FinalizationEngine(self.data_engine)
        # HIDDEN BUSINESS OPERATIONS ENGINE (INTERNAL ONLY)
        from subscription_billing_support_engine import SubscriptionBillingSupportEngine
        self._subscription_billing_support_engine = SubscriptionBillingSupportEngine(
            data_engine=self.data_engine,
            event_system=self.event_system_core,
            state_management=self.state_management_core,
            auth_logic_core=self.authentication_logic_core,
            project_dashboard_ai=self.project_dashboard_ai,
            feedback_ui_core=self.feedback_ui_core,
            snapshot_rollback_core=self.snapshot_rollback_core,
            finalization_engine=self.finalization_engine
        )
        # ENTERPRISE SYSTEM CORES (C-21 to C-40)
        self.backup_sync_core = BackupSyncCore(self.data_engine)
        self.failsafe_sentry_core = FailsafeSentryCore(self.data_engine)
        self.toolchain_core = ToolchainCore()
        self.update_patch_core = UpdatePatchCore(self.data_engine)
        self.documentation_engine = DocumentationEngine(self.data_engine)
        self.accessibility_core = AccessibilityCore(self.data_engine)
        self.seo_performance_core = SEOPerformanceCore(self.data_engine)
        self.mobile_porter_core = MobilePorterCore(self.data_engine)
        self.compliance_ai = ComplianceAI(self.data_engine)
        self.conflict_resolver = ConflictResolver(self.data_engine)
        self.code_reviewer_ai = CodeReviewerAI(self.data_engine)
        self.refactor_ai = RefactorAI(self.data_engine)
        self.microservice_splitter = MicroserviceSplitter(self.data_engine)
        self.cache_manager_core = CacheManagerCore(self.data_engine)
        self.audit_logging_core = AuditLoggingCore(self.data_engine)
        self.resource_monitor_core = ResourceMonitorCore(self.data_engine)
        self.cost_optimizer_core = CostOptimizerCore(self.data_engine)
        self.translation_ai = TranslationAI(self.data_engine)
        self.benchmarking_ai = BenchmarkingAI(self.data_engine)
        self.health_check_ai = HealthCheckAI(self.data_engine)
    def __init__(self):
        self.queue = PromptQueue()
        self.feeling = FeelingDetector()
        self.guidance_advisor = GuidanceAdvisor()
        self.guidance_responder = GuidanceResponder()
        self.chat_store = ChatStore()
        self.pipeline = PipelineController()
        self.collector = HumanFeedbackCollector()
        self.analyzer = HumanFeedbackAnalyzer()
        self.learner = HumanFeedbackLearner()
        self.injector = HumanPreferenceInjector()
        self.orchestrator = Orchestrator()
        self.busy = False
        self.workspace = SharedWorkspace()
        self.bridge = HumanAIBridge()
        self.intent_sync = IntentSync()
        self.trust_layer = TrustLayer()
        self.dialogue = LiveDialogue()
        self.collab = CollaborationEngine(self.workspace, self.bridge, self.intent_sync, self.trust_layer, self.dialogue)
        self.layout_engine = LayoutEngine()
        self.screen_detector = ScreenDetector()
        self.window_manager = WindowManager(self.layout_engine, self.screen_detector)
        self.focus_engine = FocusEngine()
        self.qc_validator = QCValidator()
        self.leader_brain = LeaderBrain()
        self.coordinator_brain = CoordinatorBrain()
        self.worker_brains = WorkerBrains()
        self.brain_dialogue = BrainDialogue()
        self.capacity_manager = CapacityManager()
        self.ai_sanitizer = AISanitizer()
        self.file_processor = FileProcessor()
        self.workspace_transfer = WorkspaceTransfer()
        self.sql_connector = SQLConnector()
        self.break_detector = BreakDetector()
        self.recovery_manager = RecoveryManager()
        self.preview_monitor = PreviewMonitor(self.break_detector, self.recovery_manager)
        # Coordinator brain for approval
        self.upload_handler = UploadHandler(
            self.capacity_manager,
            self.ai_sanitizer,
            self.file_processor,
            self.coordinator_brain,
            self.workspace_transfer,
            self.sql_connector
        )
        self.vibe_leader = VibeLeaderAI()
        self.vibe_coordinator = VibeCoordinatorAI()
        self.vibe_architect = ArchitectAI()
        self.vibe_builder = BuilderAI()
        self.vibe_debugger = DebuggerAI()
        self.vibe_reviewer = ReviewerAI()
        self.vibe_discussion = DiscussionEngine(
            self.vibe_architect,
            self.vibe_builder,
            self.vibe_debugger,
            self.vibe_reviewer
        )
        self.vibe_decision = DecisionEngine(self.vibe_leader)
        self.reasoning_chain = ReasoningChain()
        self.intent_inference = IntentInference()
        self.context_predictor = ContextPredictor()
        self.solution_ranker = SolutionRanker()
        self.inference_core = InferenceCore(
            self.reasoning_chain,
            self.intent_inference,
            self.context_predictor,
            self.solution_ranker
        )
        # DATA ENGINE: Frontal Lobe / Memory Core
        self.data_engine = DataCore()
        # ODEX CORE ENGINES — All wired to Data Engine
        self.transformers_engine = TransformersEngine(self.data_engine)
        self.autoregressive_engine = AutoregressiveEngine(self.data_engine, self.transformers_engine)
        self.agentic_engine = AgenticEngine(self.data_engine, self.transformers_engine, self.autoregressive_engine)
        # ODEX SYSTEM CORES
        self.user_input_engine = UserInputEngine(self.data_engine)
        self.ai_pilot = AIPilot(self)
        self.prompt_engineering_core = PromptEngineeringCore(self.data_engine)
        self.event_system_core = EventSystemCore()
        self.state_management_core = StateManagementCore()
        self.architecture_planner = ArchitecturePlanner(self.data_engine)
        self.code_builder_engine = CodeBuilderEngine(self.data_engine)
        self.debugger_fixer = DebuggerFixer(self.data_engine)
        self.unit_testing_core = UnitTestingCore()
        self.integration_testing_core = IntegrationTestingCore()
        self.uiux_design_engine = UIUXDesignEngine(self.data_engine)
        self.database_schema_core = DatabaseSchemaCore(self.data_engine)
        self.api_orchestrator = APIOrchestrator(self.data_engine)
        self.security_hardening_core = SecurityHardeningCore(self.data_engine)
        self.cicd_deployment_core = CICDDeploymentCore(self.data_engine)
        self.memory_pipeline_core = MemoryPipelineCore(self.data_engine)
        self.learn_go_core = LearnGoCore(self.data_engine)
        self.task_queue_core = TaskQueueCore()
        self.plugin_system_core = PluginSystemCore()
        self.analytics_bi_core = AnalyticsBICore(self.data_engine)
        self.odinference_engine = ODEXInferenceEngine(self.data_engine)
        self.training_engine = TrainingEngine(self.data_engine)
        self.execution_engine = ExecutionEngine(self.data_engine)
        self.planning_engine = PlanningEngine(self.data_engine)
        self.control_engine = ControlEngine(self.data_engine)
        self.communication_engine = CommunicationEngine(self.data_engine)
        self.observation_engine = ObservationEngine(self.data_engine)
        self.adaptation_engine = AdaptationEngine(self.data_engine)
        self.safety_engine = SafetyEngine(self.data_engine)

    def receive_input(self, prompt):
        # ALL INPUT FLOWS THROUGH DATA ENGINE
        self.data_engine.receive_data(prompt, source="user_input")
        self.data_engine.working_memory.update(prompt=prompt)
        self.data_engine.preference_memory.set_preference("last_prompt", prompt)
        self.data_engine.sql_bridge.save_record("input_log", {"prompt": prompt})
        self.data_engine.vector_bridge.similarity_search(prompt)
        self.queue.add_prompt(prompt)
        self.chat_store.store_prompt(prompt)
        self.dialogue.human_say(prompt)

    def process_next(self):
        if self.busy or not self.queue.has_tasks():
            return
        prompt = self.queue.get_next_prompt()
        # ALL PROCESSING FLOWS THROUGH DATA ENGINE
        self.data_engine.receive_data(prompt, source="task_process")
        self.data_engine.memory_guard.validate({"prompt": prompt})
        self.data_engine.sql_bridge.save_record("process_log", {"prompt": prompt})
        self.data_engine.vector_bridge.similarity_search(prompt)
        self.dialogue.human_say(f"Task: {prompt}")
        # --- MULTI-AI TRANSFORMERS ENGINE THINKING ---
        transformers_result = self.transformers_engine.think(prompt)
        self.dialogue.ai_say(f"[TRANSFORMERS ENGINE] → Multi-AI thinking engaged...")
        for msg in transformers_result["discussion"]:
            self.dialogue.ai_say(msg)
        self.dialogue.ai_say(f"[LEADER AI] Objective: {transformers_result['objective']}")
        self.dialogue.ai_say(f"[COORDINATOR AI] Tasks: {transformers_result['tasks']}")
        self.dialogue.ai_say(f"[ARCHITECT AI] Design: {transformers_result['design']}")
        self.dialogue.ai_say(f"[BUILDER AI] Code: {transformers_result['code']}")
        self.dialogue.ai_say(f"[DEBUGGER AI] Debugged: {transformers_result['debugged']}")
        self.dialogue.ai_say(f"[REVIEWER AI] Reviewed: {transformers_result['reviewed']}")
        self.dialogue.ai_say(f"[LEADER AI] Final Approval: {transformers_result['approved']}")
        # --- AGENTIC ENGINE: Autonomous multi-agent execution ---
        agentic_result = self.agentic_engine.run(prompt)
        self.dialogue.ai_say(f"[AGENTIC ENGINE] → Autonomous agents running...")
        self.dialogue.ai_say(f"[GOAL] {agentic_result['goal']}")
        self.dialogue.ai_say(f"[STRATEGY] {agentic_result['strategy']}")
        self.dialogue.ai_say(f"[RESEARCH] {agentic_result['research']}")
        self.dialogue.ai_say(f"[BUILD] {agentic_result['build']}")
        for step in agentic_result['exec_results']:
            self.dialogue.ai_say(f"[EXECUTOR] {step}")
        for eval_msg in agentic_result['evals']:
            self.dialogue.ai_say(f"[EVALUATOR] {eval_msg}")
        self.dialogue.ai_say(f"[RECOVERY] {agentic_result['recovery']}")
        self.dialogue.ai_say(f"[TOOL] {agentic_result['tool_result']}")
        self.dialogue.ai_say(f"[FEEDBACK] {agentic_result['feedback']}")
        self.dialogue.ai_say(f"[CONTEXT] {agentic_result['context']}")
        for step in agentic_result['ar_steps']:
            self.dialogue.ai_say(f"[AUTOREGRESSIVE ENGINE] {step}")
        self.dialogue.ai_say(f"[FINAL OUTPUT] {agentic_result['ar_final']}")
        # Store result in Data Engine (memory, vector, SQL, preferences)
        self.data_engine.receive_data(agentic_result['ar_final'], source="output")
        self.data_engine.long_term_memory.add_output(agentic_result['ar_final'])
        self.data_engine.sql_bridge.save_record("output_log", {"proof": agentic_result['ar_final']})
        self.data_engine.memory_guard.clean_duplicates(self.data_engine.long_term_memory.saved_outputs)
        self.data_engine.vector_bridge.similarity_search(agentic_result['ar_final'])
        self.data_engine.preference_memory.set_preference("last_output", agentic_result['ar_final'])
        # QC validation before final output
        self.qc_validator.validate(self.layout_engine, self.window_manager.windows)
        self.dialogue.ai_say(f"Proof: {agentic_result['ar_final']}")
        self.busy = False

    def interrupt(self, new_prompt):
        # Accepts new prompt, reroutes as needed
        self.receive_input(new_prompt)
        self.busy = False

    def run(self):
        print("ODEX MAIN ENGINE READY. Type your prompt (or 'exit' to quit):")
        while True:
            if not self.busy and self.queue.has_tasks():
                self.busy = True
                self.process_next()
            user_input = input("Prompt > ")
            if user_input.strip().lower() == "exit":
                break
            if user_input.strip():
                self.receive_input(user_input)
                self.busy = False

    def check_preview(self, preview_status):
        self.preview_monitor.check(preview_status)

    def handle_upload(self, uploads):
        self.upload_handler.handle_upload(uploads)






