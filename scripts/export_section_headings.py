import json
import re


input_path = "data/acts/bns_2023_v1_sections.json"
output_path = "data/evaluation/bns_section_headings.json"


with open(input_path, "r", encoding="utf-8") as f:
    sections = json.load(f)


output = []


for section in sections:

    text = section["text"].strip()

    # Remove section number
    text = re.sub(
        r"^\d+[A-Za-z]?\.\s*",
        "",
        text
    )

    # Extract heading before dash
    parts = re.split(
        r"—|––|--",
        text,
        maxsplit=1
    )

    heading = parts[0].strip()

    output.append({
        "section": section["section"],
        "heading": heading
    })


with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False
    )


print("Sections exported:", len(output))
print("Saved:", output_path)