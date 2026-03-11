from retriever import Retriever

retriever = Retriever()

tests = [
    ("career advice for Aries", "career_guidance"),
    ("Venus influence on love", "planetary_impacts"),
    ("spiritual journey for Taurus", "spiritual_guidance"),
]

correct = 0

for query, expected in tests:

    docs = retriever.search(query)

    sources = [d["source"] for d in docs]

    print("\nQuery:", query)
    print("Retrieved:", sources)
    print("Expected:", expected)

    if expected in sources:
        correct += 1

accuracy = correct / len(tests)

print("\nRetrieval Accuracy:", accuracy)