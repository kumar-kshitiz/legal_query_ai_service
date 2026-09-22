from app.retrieval.hybrid_retriever import (
    HybridLegalRetriever
)


retriever = HybridLegalRetriever()


query = input(
    "Enter legal query: "
)


results = retriever.search(
    query,
    limit=5
)


print("\n===== HYBRID RESULTS =====\n")


for i, result in enumerate(
    results,
    start=1
):

    print(
        f"Result {i}"
    )

    print(
        "Section:",
        result["section"]
    )

    print(
        "Fusion Score:",
        round(
            result["score"],
            6
        )
    )

    print(
        "Text:",
        result["payload"].get(
            "text",
            ""
        )[:300]
    )

    print(
        "\n-------------------\n"
    )