def split_section(
    text: str,
    max_words: int = 250,
    overlap_words: int = 40
) -> list[str]:

    words = text.split()

    if len(words) <= max_words:
        return [text]

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + max_words,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap_words

    return chunks


def build_chunks(
    sections: list[dict],
    document_id: str,
    act_name: str
) -> list[dict]:

    chunks = []

    for section in sections:

        parts = split_section(
            section["text"]
        )

        for i, part in enumerate(parts):

            chunk_id = (
                f"{document_id}_"
                f"sec_{section['section']}_"
                f"chunk_{i}"
            )

            chunks.append({
                "chunk_id": chunk_id,

                "document_id": document_id,

                "act_name": act_name,

                "section": section["section"],

                "chapter": section["chapter"],

                "chunk_index": i,

                "text": part
            })

    return chunks