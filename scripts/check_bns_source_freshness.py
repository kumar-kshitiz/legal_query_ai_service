import json

from pathlib import Path

from app.safety.source_freshness_checker import (
    OfficialSourceChecker
)


METADATA_PATH = Path(
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
# Check source
# ==============================================

checker = OfficialSourceChecker()


print(
    "\n===================================="
)

print(
    "OFFICIAL SOURCE FRESHNESS CHECK"
)

print(
    "===================================="
)


print(
    "Document:",
    metadata.get(
        "document_id"
    )
)


print(
    "Source:",
    metadata.get(
        "source_url"
    )
)


print(
    "\nChecking official source..."
)


result = checker.verify(
    metadata
)


# ==============================================
# Verification failed
# ==============================================

if not result.get(
    "success"
):

    print(
        "\n❌ Source verification failed."
    )


    print(
        "Reason:",
        result.get(
            "message"
        )
    )


    raise SystemExit(
        1
    )


# ==============================================
# Show hashes
# ==============================================

print(
    "\nStored hash:"
)

print(
    result[
        "local_hash"
    ]
)


print(
    "\nOfficial source hash:"
)

print(
    result[
        "remote_hash"
    ]
)


# ==============================================
# Apply metadata update
# ==============================================

metadata = checker.apply_result(
    metadata,
    result
)


# ==============================================
# Save
# ==============================================

with open(
    METADATA_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=2,
        ensure_ascii=False
    )


# ==============================================
# Result
# ==============================================

if result[
    "changed"
]:

    print(
        "\n⚠️ OFFICIAL SOURCE CHANGED"
    )


    print(
        "Current active document "
        "was NOT replaced."
    )


    print(
        "Human review required."
    )


    print(
        "Pending source hash:"
    )


    print(
        metadata.get(
            "pending_source_hash"
        )
    )


else:

    print(
        "\n✅ OFFICIAL SOURCE MATCHES"
    )


    print(
        "Freshness timestamp updated."
    )


    print(
        "Last checked:"
    )


    print(
        metadata.get(
            "last_checked_at"
        )
    )


    print(
        "Next check:"
    )


    print(
        metadata.get(
            "next_check_at"
        )
    )


print(
    "\nMetadata saved:"
)

print(
    METADATA_PATH
)