import json

from app.ingestion.section_chunker import (
    extract_sections
)


txt_path = "data/acts/bns_2023_v1.txt"

output_path = (
    "data/acts/bns_2023_v1_sections.json"
)


with open(
    txt_path,
    "r",
    encoding="utf-8"
) as f:

    text = f.read()


sections = extract_sections(text)


print("\n===== SECTION VALIDATION =====\n")

print(
    "Total sections detected:",
    len(sections)
)


numbers = [
    int(s["section"])
    for s in sections
]


# Check duplicates
duplicates = []

seen = set()

for n in numbers:

    if n in seen:
        duplicates.append(n)

    seen.add(n)


# Check missing sections
missing = []

if numbers:

    for n in range(
        1,
        max(numbers) + 1
    ):

        if n not in seen:
            missing.append(n)


print(
    "First section:",
    numbers[0] if numbers else None
)

print(
    "Last section:",
    numbers[-1] if numbers else None
)

print(
    "Duplicates:",
    duplicates
)

print(
    "Missing sections:",
    missing
)


with open(
    output_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        sections,
        f,
        indent=2,
        ensure_ascii=False
    )


print(
    "\nSaved:",
    output_path
)