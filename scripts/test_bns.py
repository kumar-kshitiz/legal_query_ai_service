import json
from app.ingestion.text_cleaner import clean_text

from app.ingestion.pdf_parser import (
    extract_pdf_text,
    get_file_hash,
    save_text
)


pdf_path = "data/acts/bns_2023_v1.pdf"
json_path = "data/acts/bns_2023_v1.json"
txt_path = "data/acts/bns_2023_v1.txt"


# 1. Calculate PDF hash
file_hash = get_file_hash(pdf_path)

print("SHA256:")
print(file_hash)


# 2. Extract text
raw_text = extract_pdf_text(pdf_path)

cleaned_text = clean_text(raw_text)

save_text(
    cleaned_text,
    txt_path
)

print("\nRaw characters:")
print(len(raw_text))

print("\nCleaned characters:")
print(len(cleaned_text))

# 4. Update JSON metadata
with open(json_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

metadata["content_hash"] = file_hash


with open(json_path, "w", encoding="utf-8") as f:
    json.dump(
        metadata,
        f,
        indent=2,
        ensure_ascii=False
    )


print("\nDone.")
print("Text saved to:", txt_path)
print("Hash added to JSON.")