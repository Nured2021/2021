from .brain_registry import BRAINS
from .stabilizer import BrainStabilizer


class BrainSystem:
    def __init__(self):
        self.stabilizer = BrainStabilizer(BRAINS)

    def run(self):
        return self.stabilizer.stabilize()

    def get_all(self):
        return {
            "brains": BRAINS,
            "count": len(BRAINS),
            "status": "active",
        }
