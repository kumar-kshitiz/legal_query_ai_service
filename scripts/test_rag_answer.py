from app.retrieval.safe_hybrid_retriever import (
    SafeHybridLegalRetriever
)

from app.rag.legal_answer_generator import (
    LegalAnswerGenerator
)


QUERY = (
    "What is the punishment for murder?"
)


# ==============================================
# Load components
# ==============================================

retriever = (
    SafeHybridLegalRetriever()
)


generator = (
    LegalAnswerGenerator()
)


# ==============================================
# Retrieve evidence
# ==============================================

print(
    "\nRetrieving legal evidence..."
)


results = retriever.search(
    QUERY,
    limit=3
)


print(
    "\nRetrieved sections:"
)


for result in results:

    print(
        "-",
        result.get(
            "section"
        )
    )


# ==============================================
# Generate answer
# ==============================================

print(
    "\nGenerating grounded answer..."
)


answer = generator.generate(

    QUERY,

    results
)


# ==============================================
# Output
# ==============================================

print(
    "\n===================================="
)

print(
    "GROUNDED LEGAL ANSWER"
)

print(
    "===================================="
)


print(
    "Question:"
)

print(
    QUERY
)


print(
    "\nAnswer:"
)

print(
    answer.get(
        "answer"
    )
)


print(
    "\nCited sections:",
    answer.get(
        "cited_sections"
    )
)


print(
    "Human review:",
    answer.get(
        "needs_human_review"
    )
)


print(
    "Reason:",
    answer.get(
        "reason"
    )
)