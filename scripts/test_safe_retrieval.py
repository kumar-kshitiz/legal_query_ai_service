from app.retrieval.safe_hybrid_retriever import (
    SafeHybridLegalRetriever,
    LegalKnowledgeUnavailableError,
)


QUERY = (
    "What is the punishment for murder?"
)


print(
    "\n===================================="
)

print(
    "SAFE LEGAL RETRIEVAL TEST"
)

print(
    "===================================="
)


retriever = (
    SafeHybridLegalRetriever()
)


# ==============================================
# Freshness state
# ==============================================

eligibility = (
    retriever.check_eligibility()
)


print(
    "\nEligible:",
    eligibility[
        "eligible_for_retrieval"
    ]
)


# ==============================================
# Retrieval
# ==============================================

try:

    results = retriever.search(
        QUERY,
        limit=3
    )


except LegalKnowledgeUnavailableError as e:

    print(
        "\n❌ RETRIEVAL BLOCKED"
    )

    print(
        str(e)
    )

    raise SystemExit(
        1
    )


print(
    "\n✅ RETRIEVAL ALLOWED"
)


print(
    "\nQuery:"
)

print(
    QUERY
)


print(
    "\nResults:"
)


for i, result in enumerate(
    results,
    start=1
):

    print(
        "\nRank:",
        i
    )

    print(
        "Section:",
        result.get(
            "section"
        )
    )

    print(
        "Score:",
        round(
            result.get(
                "rerank_score",
                0
            ),
            4
        )
    )


    source = result.get(
        "legal_source",
        {}
    )


    print(
        "Version:",
        source.get(
            "version"
        )
    )

    print(
        "Verified:",
        source.get(
            "verified"
        )
    )

    print(
        "Last checked:",
        source.get(
            "last_checked_at"
        )
    )