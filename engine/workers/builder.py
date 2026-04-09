from generator.project_builder import ProjectBuilder

class BuilderWorker:
    def execute(self, task):
        builder = ProjectBuilder()
        result = builder.build_project(task)
        return f"Project built: {result}"





