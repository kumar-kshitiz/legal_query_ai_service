import json

from app.embeddings.embedder import LegalEmbedder
from app.vectorstore.qdrant_store import LegalVectorStore
from app.retrieval.bm25_retriever import BM25LegalRetriever


path = "data/evaluation/bns_queries_realistic.json"


with open(path, "r", encoding="utf-8") as f:
    tests = json.load(f)


embedder = LegalEmbedder()
vector_store = LegalVectorStore()
bm25 = BM25LegalRetriever()


for test in tests:

    q = test["query"]
    expected = str(test["expected_section"])


    # -------------------------
    # Dense Top 20
    # -------------------------

    vec = embedder.embed_query(q)

    dense_results = vector_store.search(
        vec,
        limit=20
    )

    dense_sections = []

    for r in dense_results:

        sec = str(
            r.payload.get("section")
        )

        if sec not in dense_sections:
            dense_sections.append(sec)


    # -------------------------
    # BM25 Top 20
    # -------------------------

    bm25_results = bm25.search(
        q,
        limit=20
    )

    bm25_sections = [
        str(r["section"])
        for r in bm25_results
    ]


    # -------------------------
    # Find ranks
    # -------------------------

    dense_rank = None
    bm25_rank = None


    if expected in dense_sections:

        dense_rank = (
            dense_sections.index(expected)
            + 1
        )


    if expected in bm25_sections:

        bm25_rank = (
            bm25_sections.index(expected)
            + 1
        )


    print("\n--------------------------------")

    print("Query:", q)

    print("Expected:", expected)

    print(
        "Dense rank:",
        dense_rank
    )

    print(
        "BM25 rank:",
        bm25_rank
    )


    if (
        dense_rank is None
        and bm25_rank is None
    ):

        print(
            "❌ Missing from both candidate sets"
        )

    else:

        print(
            "✅ Candidate available for reranking"
        )