class TaskQueueCore:
    def __init__(self):
        self.queue = []

    def add_task(self, task):
        self.queue.append(task)

    def get_next(self):
        return self.queue.pop(0) if self.queue else None

    # Backward-compatible queue API used by MainEngine
    def add_prompt(self, prompt):
        self.add_task(prompt)

    def has_tasks(self):
        return len(self.queue) > 0

    def get_next_prompt(self):
        return self.get_next()






