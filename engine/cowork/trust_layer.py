class TrustLayer:
    def is_override(self, user_input):
        # Detect strong correction/override
        keywords = ["override", "no", "stop", "change", "reject"]
        return any(word in user_input.lower() for word in keywords)
    def acknowledge(self, message):
        print(f"[TRUST] {message}")






