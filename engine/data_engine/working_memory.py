"""
WORKING MEMORY — Short-term, fast memory
Stores what is active right now: current prompt, task, build stage, active files, recent instructions.
"""

class WorkingMemory:
    def __init__(self):
        self.active_prompt = None
        self.current_task = None
        self.build_stage = None
        self.active_files = []
        self.recent_instructions = []

    def update(self, prompt=None, task=None, build_stage=None, files=None, instruction=None):
        if prompt is not None:
            self.active_prompt = prompt
        if task is not None:
            self.current_task = task
        if build_stage is not None:
            self.build_stage = build_stage
        if files is not None:
            self.active_files = files
        if instruction is not None:
            self.recent_instructions.append(instruction)
            if len(self.recent_instructions) > 10:
                self.recent_instructions.pop(0)

    def get_state(self):
        return {
            "prompt": self.active_prompt,
            "task": self.current_task,
            "build_stage": self.build_stage,
            "active_files": self.active_files,
            "recent_instructions": self.recent_instructions,
        }






