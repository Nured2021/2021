"""
CONTEXT LINKER — Connects related data together
Links uploads, bugs, preferences, fixes, etc. to relevant modules.
"""

class ContextLinker:
    def __init__(self, data_core):
        self.data_core = data_core
        self.links = []

    def link(self, source, target, relation):
        self.links.append({"source": source, "target": target, "relation": relation})

    def get_links(self, filter_by=None):
        if filter_by:
            return [l for l in self.links if l["relation"] == filter_by]
        return self.links






