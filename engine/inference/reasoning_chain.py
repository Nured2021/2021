class ReasoningChain:
    def reason(self, user_input, feeling_state, memory, workspace_state, queue):
        # Step-by-step reasoning
        steps = [
            f"Read input: {user_input}",
            f"Feeling: {feeling_state}",
            f"Memory: {memory}",
            f"Workspace: {workspace_state}",
            f"Queue: {queue}"
        ]
        print("[INFERENCE] → Reading user meaning...")
        for s in steps:
            print(f"[INFERENCE] → {s}")
        return steps






