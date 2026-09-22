import json

from app.retrieval.hybrid_retriever import HybridLegalRetriever


path = "data/evaluation/bns_queries_realistic.json"


with open(
    path,
    "r",
    encoding="utf-8"
) as f:
    tests = json.load(f)


retriever = HybridLegalRetriever()


top1 = 0
top3 = 0
top5 = 0


print(
    "Total benchmark queries:",
    len(tests)
)


for test in tests:

    q = test["query"]

    expected = str(
        test["expected_section"]
    )


    results = retriever.search(
        q,
        limit=5
    )


    sections = [
        str(r["section"])
        for r in results
    ]


    # -------------------------
    # Metrics
    # -------------------------

    if expected in sections[:1]:
        top1 += 1

    if expected in sections[:3]:
        top3 += 1

    if expected in sections[:5]:
        top5 += 1


    # -------------------------
    # Find correct rank
    # -------------------------

    rank = None


    for i, section in enumerate(
        sections,
        start=1
    ):

        if section == expected:
            rank = i
            break


    # -------------------------
    # Print only weak cases
    # -------------------------

    if rank != 1:

        print("\n-------------------------")

        print(
            "Query:",
            q
        )

        print(
            "Expected:",
            expected
        )

        print(
            "\nTop results:"
        )


        for i, result in enumerate(
            results,
            start=1
        ):

            print(
                i,
                "Section:",
                result["section"],
                "Rerank score:",
                round(
                    result.get(
                        "rerank_score",
                        0
                    ),
                    4
                )
            )


        print(
            "Correct section rank:",
            rank
        )


        if rank is None:

            print(
                "❌ NOT FOUND"
            )

        else:

            print(
                "⚠️ NEEDS IMPROVEMENT"
            )


# -------------------------
# Final metrics
# -------------------------

n = len(tests)


print(
    "\n===== HYBRID RETRIEVAL EVALUATION ====="
)


print(
    "Top-1 Accuracy:",
    round(
        top1 / n * 100,
        2
    ),
    "%"
)


print(
    "Top-3 Accuracy:",
    round(
        top3 / n * 100,
        2
    ),
    "%"
)


print(
    "Top-5 Accuracy:",
    round(
        top5 / n * 100,
        2
    ),
    "%"
)