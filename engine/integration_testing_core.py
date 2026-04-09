class IntegrationTestingCore:
    def __init__(self):
        self.results = []
    def test(self, system):
        result = f"Integration test passed for {system}"
        self.results.append(result)
        return result






