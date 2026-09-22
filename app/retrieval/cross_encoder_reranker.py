from sentence_transformers import CrossEncoder


MODEL_NAME = "BAAI/bge-reranker-base"


class LegalCrossEncoderReranker:

    def __init__(self):

        self.model = CrossEncoder(
            MODEL_NAME
        )


    def rerank(
        self,
        query: str,
        candidates: list,
        limit: int = 5
    ):

        if not candidates:
            return []


        pairs = []

        for candidate in candidates:

            text = candidate[
                "payload"
            ].get(
                "text",
                ""
            )

            pairs.append(
                [
                    query,
                    text
                ]
            )


        scores = self.model.predict(
            pairs
        )


        ranked = []


        for candidate, score in zip(
            candidates,
            scores
        ):

            candidate = candidate.copy()

            candidate[
                "rerank_score"
            ] = float(score)

            ranked.append(
                candidate
            )


        ranked.sort(
            key=lambda x:
            x["rerank_score"],
            reverse=True
        )


        return ranked[:limit]