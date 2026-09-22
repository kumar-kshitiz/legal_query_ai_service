from app.embeddings.embedder import (
    LegalEmbedder
)

from app.vectorstore.qdrant_store import (
    LegalVectorStore
)


query = input(
    "Enter legal query: "
)


print("\nGenerating query embedding...")


embedder = LegalEmbedder()

query_vector = embedder.embed_query(
    query
)


store = LegalVectorStore()


results = store.search(
    query_vector,
    limit=5
)


print("\n===== SEARCH RESULTS =====\n")


for i, result in enumerate(
    results,
    start=1
):

    p = result.payload

    print(
        f"Result {i}"
    )

    print(
        "Score:",
        round(result.score, 4)
    )

    print(
        "Act:",
        p.get("act_name")
    )

    print(
        "Section:",
        p.get("section")
    )

    print(
        "Chapter:",
        p.get("chapter")
    )

    print(
        "Chunk:",
        p.get("chunk_index")
    )

    print(
        "\nText:"
    )

    print(
        p.get("text", "")[:700]
    )

    print(
        "\n----------------------------\n"
    )