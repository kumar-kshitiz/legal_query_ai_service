import json
import re

from rank_bm25 import BM25Okapi


class BM25LegalRetriever:

    def __init__(
        self,
        chunks_path: str =
        "data/acts/bns_2023_v1_chunks.json"
    ):

        with open(
            chunks_path,
            "r",
            encoding="utf-8"
        ) as f:
            self.chunks = json.load(f)

        self.tokenized_docs = [
            self.tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_docs
        )


    def tokenize(
        self,
        text: str
    ) -> list[str]:

        return re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )


    def search(
        self,
        query: str,
        limit: int = 5
    ):

        tokens = self.tokenize(query)

        scores = self.bm25.get_scores(
            tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )


        results = []
        seen_sections = set()


        for i in ranked_indices:

            chunk = self.chunks[i]

            section = str(
                chunk["section"]
            )

            if section in seen_sections:
                continue

            seen_sections.add(section)

            results.append({
                "section": section,
                "score": float(scores[i]),
                "text": chunk["text"],
                "chunk_id": chunk["chunk_id"]
            })

            if len(results) == limit:
                break


        return results