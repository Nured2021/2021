class DecisionEngine:
    def __init__(self, leader):
        self.leader = leader
    def decide(self, discussion):
        print("[DECISION] Collecting team opinions...")
        return self.leader.decide(discussion)






