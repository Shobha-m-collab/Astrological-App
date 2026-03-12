class MemoryManager:
    def __init__(self, max_turns=4):
        self.sessions = {}
        self.max_turns = max_turns  # Kept small (4) to keep LLM context light & fast

    def get_history(self, session_id: str):
        return self.sessions.get(session_id, [])

    def save_turn(self, session_id: str, user_msg: str, assistant_msg: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        self.sessions[session_id].append({
            "user": user_msg,
            "assistant": assistant_msg
        })

        # Memory control: Keep only the last N turns
        self.sessions[session_id] = self.sessions[session_id][-self.max_turns:]