class EventSystemCore:
    def __init__(self):
        self.events = []
    def trigger(self, event):
        self.events.append(event)
        return f"Event triggered: {event}"






