import hashlib
from pathlib import Path

import fitz


def get_file_hash(file_path: str) -> str:
    sha = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)

    return sha.hexdigest()


def extract_pdf_text(file_path: str) -> str:
    doc = fitz.open(file_path)

    pages = []

    for page in doc:
        text = page.get_text("text")
        pages.append(text)

    doc.close()

    return "\n".join(pages)


def save_text(text: str, output_path: str):
    Path(output_path).write_text(
        text,
        encoding="utf-8"
    )