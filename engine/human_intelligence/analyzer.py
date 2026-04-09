class HumanFeedbackAnalyzer:
    def compare_outputs(self, ai_output, human_edit):
        # Simple diff logic (placeholder)
        diffs = []
        for key in ai_output:
            if key in human_edit and ai_output[key] != human_edit[key]:
                diffs.append((key, ai_output[key], human_edit[key]))
        return diffs






