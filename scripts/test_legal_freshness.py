import json

from app.safety.legal_freshness import (
    LegalFreshnessChecker
)


METADATA_PATH = (
    "data/acts/"
    "bns_2023_v1.json"
)


# ==============================================
# Load metadata
# ==============================================

with open(
    METADATA_PATH,
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)


# ==============================================
# Check freshness
# ==============================================

checker = LegalFreshnessChecker()


result = checker.validate(
    metadata
)


# ==============================================
# Output
# ==============================================

print(
    "\n===================================="
)

print(
    "LEGAL FRESHNESS CHECK"
)

print(
    "===================================="
)


print(
    "Document:",
    result[
        "document_id"
    ]
)


print(
    "Version:",
    result[
        "version"
    ]
)


print(
    "\nChecks:"
)


for name, check in result[
    "checks"
].items():

    symbol = (
        "✅"
        if check[
            "passed"
        ]
        else "❌"
    )


    print(
        symbol,
        name,
        "-",
        check[
            "message"
        ]
    )


print(
    "\nEligible for retrieval:",
    result[
        "eligible_for_retrieval"
    ]
)