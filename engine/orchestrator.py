from workers.builder import BuilderWorker
from workers.debugger import DebuggerWorker
from workers.tester import TesterWorker
from workers.deployer import DeployerWorker

class Orchestrator:
    def __init__(self):
        self.workers = {
            'builder': BuilderWorker(),
            'debugger': DebuggerWorker(),
            'tester': TesterWorker(),
            'deployer': DeployerWorker(),
        }
        self.queue = []
        self.state = {}

    def assign_task(self, worker_type, task):
        worker = self.workers.get(worker_type)
        if not worker:
            raise Exception(f"Unknown worker: {worker_type}")
        result = worker.execute(task)

from main_engine import MainEngine
import time

def run_orchestrator(prompt, socketio=None):
    logs = []
    active_engines = []
    stages = []
    result = None
    main = MainEngine()

    def emit_log(engine, stage, status, message):
        log = {"engine": engine, "stage": stage, "status": status, "message": message}
        logs.append(log)
        if socketio:
            socketio.emit("log", log)

    # STAGE 1: INPUT CAPTURE
    emit_log("orchestrator", "plan", "running", f"Prompt received: {prompt}")
    active_engines.append("orchestrator")
    stages.append("input_capture")
    time.sleep(0.1)

    # STAGE 2: MEMORY + CONTEXT LOAD
    emit_log("memory", "context", "running", "Loading project memory")
    active_engines.append("memory")
    stages.append("memory_context")
    time.sleep(0.1)

    # STAGE 3: INTENT + INFERENCE
    emit_log("inference", "reason", "running", "Analyzing intent")
    active_engines.append("inference")
    stages.append("intent_inference")
    time.sleep(0.1)

    # STAGE 4: TASK BREAKDOWN
    emit_log("queue", "task", "running", "Breaking down tasks")
    active_engines.append("queue")
    stages.append("task_breakdown")
    time.sleep(0.1)

    # STAGE 5: GENERATION / BUILD
    emit_log("generator", "build", "running", "Generating output")
    active_engines.append("generator")
    stages.append("generation")
    time.sleep(0.1)

    # STAGE 6: PREVIEW + CHECK
    emit_log("preview_control", "preview", "running", "Preparing preview")
    active_engines.append("preview_control")
    stages.append("preview")
    time.sleep(0.1)

    # STAGE 7: SAVE + RETURN
    emit_log("storage", "save", "done", "Saving result")
    active_engines.append("storage")
    stages.append("save")
    time.sleep(0.1)

    # Simulate real engine output (replace with actual engine calls as needed)
    result = {
        "output": f"ODEX generated result for: {prompt}",
        "engines": active_engines,
        "stages": stages
    }

    return {
        "status": "success",
        "prompt": prompt,
        "active_engines": active_engines,
        "stages": stages,
        "result": result,
        "logs": logs
    }






