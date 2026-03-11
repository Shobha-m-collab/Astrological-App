sessions = {}


def get_history(session_id):

    return sessions.get(session_id, [])


def save_turn(session_id, user_msg, assistant_msg):

    sessions.setdefault(session_id, []).append({
        "user": user_msg,
        "assistant": assistant_msg
    })

    # keep last 5 turns (memory control)
    sessions[session_id] = sessions[session_id][-5:]