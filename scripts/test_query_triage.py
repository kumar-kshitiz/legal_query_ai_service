from app.retrieval.safe_hybrid_retriever import (
    SafeHybridLegalRetriever
)

from app.triage.query_triage import (
    LegalQueryTriage
)


# ==================================================
# Components
# ==================================================

retriever = (
    SafeHybridLegalRetriever()
)


triage = (
    LegalQueryTriage()
)


# ==================================================
# Test cases
# ==================================================

queries = [

    "What is the punishment for murder?",

    "Someone secretly took my mobile phone without permission. What law applies?",

    "Is this illegal?",

    (
        "A person threatened me, then took my money, "
        "and later another person helped him hide it. "
        "What offences could apply and what should I do?"
    ),

    (
        "Someone is threatening to kill me right now. "
        "What legal action can I take?"
    ),

    (
        "A minor has reported sexual assault. "
        "What legal provisions apply?"
    ),
]


# ==================================================
# Run
# ==================================================

for query in queries:

    print(
        "\n===================================="
    )


    print(
        "QUERY:"
    )


    print(
        query
    )


    # ----------------------------------------------
    # Retrieve first
    # ----------------------------------------------

    results = (
        retriever.search(
            query,
            limit=5
        )
    )


    # ----------------------------------------------
    # Triage
    # ----------------------------------------------

    decision = (
        triage.classify(
            query,
            results
        )
    )


    print(
        "\nROUTE:",
        decision.route.value.upper()
    )


    print(
        "Confidence:",
        decision.confidence
    )


    print(
        "Sensitive:",
        decision.sensitive
    )


    print(
        "Urgent:",
        decision.urgent
    )


    print(
        "Ambiguous:",
        decision.ambiguous
    )


    print(
        "Complex:",
        decision.complex
    )


    print(
        "Reasons:"
    )


    for reason in decision.reasons:

        print(
            "-",
            reason
        )