class TaskQueueCore:
    def __init__(self):
        self.queue = []
    def add_task(self, task):
        self.queue.append(task)
    def get_next(self):
        return self.queue.pop(0) if self.queue else None






