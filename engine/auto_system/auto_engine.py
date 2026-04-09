from .brain_registry import BRAINS


class AutoEngine:
    def __init__(self):
        self.brains = BRAINS

    def generate_backend_routes(self):
        routes = []
        for brain in self.brains:
            route = f"/{brain.lower()}/action"
            routes.append(route)
        return routes

    def generate_ui_components(self):
        components = []
        for brain in self.brains:
            components.append(f"{brain}Panel")
        return components

    def generate_dashboard_panels(self):
        panels = []
        for brain in self.brains:
            panels.append(f"{brain}Widget")
        return panels

    def connect_all(self):
        return {
            "brains": len(self.brains),
            "status": "connected",
            "mode": "auto",
        }

    def run(self):
        return {
            "routes": self.generate_backend_routes(),
            "components": self.generate_ui_components(),
            "panels": self.generate_dashboard_panels(),
            "system": self.connect_all(),
        }
