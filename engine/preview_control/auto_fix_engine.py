from preview_control.ai_team.leader import LeaderAI
from preview_control.ai_team.coordinator import CoordinatorAI
from preview_control.ai_team.scanners import Scanners
from preview_control.ai_team.debuggers import Debuggers
from preview_control.ai_team.fixers import Fixers
from preview_control.ai_team.qc_agents import QCAgents
from preview_control.ai_team.communicator import Communicator

class AutoFixEngine:
    def __init__(self):
        self.leader = LeaderAI()
        self.coordinator = CoordinatorAI()
        self.scanners = Scanners()
        self.debuggers = Debuggers()
        self.fixers = Fixers()
        self.qc = QCAgents()
        self.communicator = Communicator()
    def run_fix_pipeline(self, issue):
        self.communicator.inform_user("⚠️ Preview paused — system issue detected\nDon’t worry, I’m fixing it now\nEstimated time: 10–30 seconds")
        self.leader.decide(issue)
        self.coordinator.assign(issue)
        self.scanners.scan(issue)
        self.debuggers.debug(issue)
        self.fixers.fix(issue)
        self.qc.check(issue)
        self.communicator.inform_user("[PREVIEW] Restarting...")






