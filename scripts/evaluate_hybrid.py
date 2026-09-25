import json

from app.retrieval.hybrid_retriever import (
    HybridLegalRetriever
)


PATH = (
    "data/evaluation/"
    "bns_queries_realistic.json"
)


with open(
    PATH,
    "r",
    encoding="utf-8"
) as f:

    tests = json.load(f)


retriever = HybridLegalRetriever()


top1 = 0
top3 = 0
top5 = 0

original_top1 = 0

improved = 0
regressed = 0


print(
    "Total benchmark queries:",
    len(tests)
)


for test in tests:

    query = test[
        "query"
    ]


    expected = str(
        test[
            "expected_section"
        ]
    )


    results = retriever.search(

        query,

        limit=5,

        disambiguate=True
    )


    sections = [

        str(
            result[
                "section"
            ]
        )

        for result
        in results
    ]


    # ==============================================
    # New metrics
    # ==============================================

    if expected in sections[:1]:

        top1 += 1


    if expected in sections[:3]:

        top3 += 1


    if expected in sections[:5]:

        top5 += 1


    # ==============================================
    # New rank
    # ==============================================

    rank = None


    for i, section in enumerate(
        sections,
        start=1
    ):

        if section == expected:

            rank = i

            break


    # ==============================================
    # Original rank before disambiguation
    # ==============================================

    original_rank = None


    for result in results:

        section = str(
            result[
                "section"
            ]
        )


        if section == expected:

            original_rank = (
                result.get(
                    "original_rank"
                )
            )

            break


    # Candidates outside top3 do not have
    # original_rank attached.
    if (
        original_rank is None
        and
        rank is not None
        and
        rank > 3
    ):

        original_rank = rank


    if original_rank == 1:

        original_top1 += 1


    # ==============================================
    # Improvement / regression tracking
    # ==============================================

    if (
        original_rank is not None
        and
        rank is not None
    ):

        if rank < original_rank:

            improved += 1


        elif rank > original_rank:

            regressed += 1


    # ==============================================
    # Print interesting cases
    # ==============================================

    if (
        rank != 1
        or
        original_rank != rank
    ):

        print(
            "\n--------------------------------"
        )


        print(
            "Query:",
            query
        )


        print(
            "Expected:",
            expected
        )


        print(
            "Original rank:",
            original_rank
        )


        print(
            "New rank:",
            rank
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
                result[
                    "section"
                ],
                "| Cross:",
                round(
                    result.get(
                        "original_rerank_score",
                        result.get(
                            "rerank_score",
                            0
                        )
                    ),
                    4
                ),
                "| Heading:",
                round(
                    result.get(
                        "heading_score",
                        0
                    ),
                    4
                ),
                "| Short:",
                round(
                    result.get(
                        "short_score",
                        0
                    ),
                    4
                ),
                "| Final:",
                round(
                    result.get(
                        "disambiguation_score",
                        0
                    ),
                    4
                )
            )


# ==============================================
# Final metrics
# ==============================================

n = len(
    tests
)


print(
    "\n===================================="
)

print(
    "HYBRID + LEGAL DISAMBIGUATION"
)

print(
    "===================================="
)


print(
    "Original Top-1:",
    round(
        original_top1
        /
        n
        *
        100,
        2
    ),
    "%"
)


print(
    "New Top-1:",
    round(
        top1
        /
        n
        *
        100,
        2
    ),
    "%"
)


print(
    "Top-3:",
    round(
        top3
        /
        n
        *
        100,
        2
    ),
    "%"
)


print(
    "Top-5:",
    round(
        top5
        /
        n
        *
        100,
        2
    ),
    "%"
)


print(
    "Queries improved:",
    improved
)


print(
    "Queries regressed:",
    regressed
)