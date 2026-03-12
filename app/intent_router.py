class IntentRouter:
    def __init__(self):
        # Using a set for O(1) ultra-fast lookups
        self.keywords = {
            "career", "job", "work",
            "love", "relationship", "marriage", "partner",
            "planet", "sun", "moon", "mars", "venus",
            "spiritual", "meditation", "karma",
            "today", "future", "month"
        }

    def should_retrieve(self, message: str) -> bool:
        """
        Returns True if the message needs astrological facts.
        Returns False for conversational meta-questions (e.g. "summarize", "why again?").
        """
        message_lower = message.lower()
        
        # Meta conversation check (don't retrieve)
        if any(meta in message_lower for meta in ["summarize", "again", "repeat", "who are you"]):
            return False

        # Knowledge check
        return any(k in message_lower for k in self.keywords)