from app.retrieval.bm25_retriever import (
    BM25LegalRetriever
)


retriever = BM25LegalRetriever()


query = input(
    "Enter legal query: "
)


results = retriever.search(
    query,
    limit=5
)


print("\n===== BM25 RESULTS =====\n")


for i, r in enumerate(
    results,
    start=1
):

    print(
        f"Result {i}"
    )

    print(
        "Section:",
        r["section"]
    )

    print(
        "Score:",
        round(
            r["score"],
            4
        )
    )

    print(
        "Text:",
        r["text"][:300]
    )

    print(
        "\n-------------------\n"
    )