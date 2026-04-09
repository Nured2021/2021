class PluginSystemCore:
    def __init__(self):
        self.plugins = []
    def add_plugin(self, plugin):
        self.plugins.append(plugin)
    def get_plugins(self):
        return self.plugins






