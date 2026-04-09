from generator.project_builder import ProjectBuilder

def input_stage(context, orchestrator):
    context['intent'] = context['prompt']
    return f"Input captured: {context['intent']}"

def plan_stage(context, orchestrator):
    context['plan'] = ["Create backend", "Create frontend", "Setup DB"]
    return f"Plan: {context['plan']}"

def architecture_stage(context, orchestrator):
    context['architecture'] = {'db': 'sqlite', 'api': 'REST'}
    return f"Architecture: {context['architecture']}"

def build_stage(context, orchestrator):
    builder_task = {'type': 'build', 'plan': context['plan'], 'architecture': context['architecture']}
    result = orchestrator.assign_task('builder', builder_task)
    return f"Build: {result}"

def debug_stage(context, orchestrator):
    debug_task = {'type': 'debug'}
    result = orchestrator.assign_task('debugger', debug_task)
    return f"Debug: {result}"

def test_stage(context, orchestrator):
    test_task = {'type': 'test'}
    result = orchestrator.assign_task('tester', test_task)
    return f"Test: {result}"

def deploy_stage(context, orchestrator):
    deploy_task = {'type': 'deploy'}
    result = orchestrator.assign_task('deployer', deploy_task)
    return f"Deploy: {result}"

def learn_stage(context, orchestrator):
    return "Learning: User edits captured."

class PipelineStages:
    def get_stages(self):
        return [
            input_stage,
            plan_stage,
            architecture_stage,
            build_stage,
            debug_stage,
            test_stage,
            deploy_stage,
            learn_stage
        ]






