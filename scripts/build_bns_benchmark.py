import json
import random


input_path = "data/evaluation/bns_section_headings.json"
output_path = "data/evaluation/bns_queries_large.json"


with open(input_path, "r", encoding="utf-8") as f:
    sections = json.load(f)


# Fixed seed so benchmark stays identical
random.seed(42)


# Pick 30 different sections
selected = random.sample(sections, 30)


queries = []


for item in selected:

    sec = str(item["section"])
    heading = item["heading"].strip().rstrip(".")


    # Create one natural-ish query from the heading
    query = f"What does the law say about {heading.lower()}?"


    queries.append({
        "query": query,
        "expected_section": sec
    })


with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        queries,
        f,
        indent=2,
        ensure_ascii=False
    )


print("Benchmark queries created:", len(queries))
print("Saved:", output_path)