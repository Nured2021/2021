class CardBuilder:
    def build_cards(self, tools):
        cards = []
        for group in tools:
            for tool in tools[group]:
                cards.append({
                    "name": tool,
                    "status": "active",
                    "type": group,
                })
        return cards
