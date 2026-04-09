class LeaderAI:
    def decide(self, discussion):
        print("[LEADER] Final decision based on team discussion.")
        for msg in discussion:
            print(f"[LEADER] Heard: {msg}")
        print("[LEADER] Decision made.")
        return "approved"






