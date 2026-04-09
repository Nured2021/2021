class FailsafeSentryCore:
    def __init__(self, data_engine):
        self.data_engine = data_engine
    def detect_failure(self, status):
        if status == "fail":
            return "Failure detected, triggering recovery"
        return "System healthy"
    def protect(self):
        return "System protection active"






