import json

from app.embeddings.embedder import LegalEmbedder
from app.vectorstore.qdrant_store import LegalVectorStore
from app.retrieval.reranker import rerank_results


path = "data/evaluation/bns_queries_realistic.json"

with open(path, "r", encoding="utf-8") as f:
    tests = json.load(f)


embedder = LegalEmbedder()
store = LegalVectorStore()


dense_top1 = 0
dense_top3 = 0
dense_top5 = 0

rerank_top1 = 0
rerank_top3 = 0
rerank_top5 = 0


for test in tests:

    q = test["query"]
    expected = str(test["expected_section"])

    vec = embedder.embed_query(q)

    # -------------------------
    # Dense search
    # -------------------------

    dense_results = store.search(
        vec,
        limit=10
    )

    # Remove duplicate sections
    dense_unique = []
    seen = set()

    for r in dense_results:

        sec = str(r.payload.get("section"))

        if sec in seen:
            continue

        seen.add(sec)
        dense_unique.append(r)

    dense_unique = dense_unique[:5]

    dense_sections = [
        str(r.payload.get("section"))
        for r in dense_unique
    ]


    # -------------------------
    # Reranked search
    # -------------------------

    reranked = rerank_results(
        q,
        dense_results
    )

    reranked = reranked[:5]

    rerank_sections = [
        str(r.payload.get("section"))
        for r in reranked
    ]


    # -------------------------
    # Dense metrics
    # -------------------------

    if expected in dense_sections[:1]:
        dense_top1 += 1

    if expected in dense_sections[:3]:
        dense_top3 += 1

    if expected in dense_sections[:5]:
        dense_top5 += 1


    # -------------------------
    # Reranker metrics
    # -------------------------

    if expected in rerank_sections[:1]:
        rerank_top1 += 1

    if expected in rerank_sections[:3]:
        rerank_top3 += 1

    if expected in rerank_sections[:5]:
        rerank_top5 += 1


    print("\n--------------------------------")

    print("Query:", q)
    print("Expected:", expected)

    print(
        "Dense:",
        dense_sections
    )

    print(
        "Reranked:",
        rerank_sections
    )


n = len(tests)


print("\n===== DENSE SEARCH =====")

print(
    "Top-1:",
    round(dense_top1 / n * 100, 2),
    "%"
)

print(
    "Top-3:",
    round(dense_top3 / n * 100, 2),
    "%"
)

print(
    "Top-5:",
    round(dense_top5 / n * 100, 2),
    "%"
)


print("\n===== RERANKED SEARCH =====")

print(
    "Top-1:",
    round(rerank_top1 / n * 100, 2),
    "%"
)

print(
    "Top-3:",
    round(rerank_top3 / n * 100, 2),
    "%"
)

print(
    "Top-5:",
    round(rerank_top5 / n * 100, 2),
    "%"
)