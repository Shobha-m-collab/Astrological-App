def should_retrieve(message):

    keywords = [
        "career",
        "love",
        "relationship",
        "planet",
        "spiritual",
        "today"
    ]

    message = message.lower()

    return any(k in message for k in keywords)