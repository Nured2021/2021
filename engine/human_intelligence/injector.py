class HumanPreferenceInjector:
    def inject(self, context, preferences):
        for key, value in preferences.items():
            context[key] = value
        return context






