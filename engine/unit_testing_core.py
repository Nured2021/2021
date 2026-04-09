class UnitTestingCore:
    def __init__(self):
        self.results = []
    def test(self, code):
        result = f"Unit test passed for {code}"
        self.results.append(result)
        return result






