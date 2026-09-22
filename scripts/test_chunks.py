import json

from app.ingestion.chunk_builder import (
    build_chunks
)


input_path = (
    "data/acts/"
    "bns_2023_v1_sections.json"
)

output_path = (
    "data/acts/"
    "bns_2023_v1_chunks.json"
)


with open(
    input_path,
    "r",
    encoding="utf-8"
) as f:

    sections = json.load(f)


chunks = build_chunks(
    sections=sections,
    document_id="bns_2023_v1",
    act_name="Bharatiya Nyaya Sanhita, 2023"
)


with open(
    output_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        chunks,
        f,
        indent=2,
        ensure_ascii=False
    )


print("Sections:", len(sections))
print("Chunks:", len(chunks))


print("\nFirst chunk:\n")

print(
    json.dumps(
        chunks[0],
        indent=2,
        ensure_ascii=False
    )
)