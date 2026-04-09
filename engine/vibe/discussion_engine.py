class DiscussionEngine:
    def __init__(self, architect, builder, debugger, reviewer):
        self.architect = architect
        self.builder = builder
        self.debugger = debugger
        self.reviewer = reviewer
    def discuss(self, prompt):
        discussion = []
        discussion.append(self.architect.plan(prompt))
        discussion.append(self.builder.suggest(prompt))
        discussion.append(self.debugger.warn(prompt))
        discussion.append(self.reviewer.validate(prompt))
        return discussion






