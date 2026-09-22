import json

from app.embeddings.embedder import LegalEmbedder
from app.vectorstore.qdrant_store import LegalVectorStore
from app.retrieval.bm25_retriever import BM25LegalRetriever
from app.retrieval.cross_encoder_reranker import (
    LegalCrossEncoderReranker
)


class HybridLegalRetriever:

    def __init__(self):

        self.embedder = LegalEmbedder()

        self.vector_store = LegalVectorStore()

        self.bm25 = BM25LegalRetriever()

        self.reranker = LegalCrossEncoderReranker()


        # --------------------------------
        # Load complete parent sections
        # --------------------------------

        sections_path = (
            "data/acts/"
            "bns_2023_v1_sections.json"
        )

        with open(
            sections_path,
            "r",
            encoding="utf-8"
        ) as f:

            sections = json.load(f)


        self.section_map = {}

        for section in sections:

            sec = str(
                section["section"]
            )

            self.section_map[sec] = section


    def get_section_text(
        self,
        section: str
    ) -> str:

        data = self.section_map.get(
            str(section)
        )

        if not data:
            return ""

        text = data.get(
            "text",
            ""
        )

        # Reranker does not need the entire
        # extremely long section.
        #
        # The beginning normally contains:
        # section number + heading + definition.
        return text[:2000]


    def search(
        self,
        query: str,
        limit: int = 5
    ):

        # =================================
        # 1. Dense retrieval
        # =================================

        query_vector = (
            self.embedder.embed_query(
                query
            )
        )


        dense_results = (
            self.vector_store.search(
                query_vector,
                limit=20
            )
        )


        dense_sections = []

        seen = set()


        for result in dense_results:

            section = str(
                result.payload.get(
                    "section"
                )
            )


            if section in seen:
                continue


            seen.add(section)


            dense_sections.append({
                "section": section,
                "dense_score": float(
                    result.score
                ),
                "payload": result.payload
            })


        # =================================
        # 2. BM25 retrieval
        # =================================

        bm25_results = (
            self.bm25.search(
                query,
                limit=20
            )
        )


        # =================================
        # 3. Reciprocal Rank Fusion
        # =================================

        fusion_scores = {}

        section_data = {}


        k = 60

        dense_weight = 1.0

        bm25_weight = 0.6


        # ---------------------------------
        # Dense contribution
        # ---------------------------------

        for rank, result in enumerate(
            dense_sections,
            start=1
        ):

            section = result[
                "section"
            ]


            score = (
                dense_weight
                /
                (k + rank)
            )


            fusion_scores[section] = (
                fusion_scores.get(
                    section,
                    0
                )
                + score
            )


            section_data[section] = (
                result
            )


        # ---------------------------------
        # BM25 contribution
        # ---------------------------------

        for rank, result in enumerate(
            bm25_results,
            start=1
        ):

            section = str(
                result[
                    "section"
                ]
            )


            score = (
                bm25_weight
                /
                (k + rank)
            )


            fusion_scores[section] = (
                fusion_scores.get(
                    section,
                    0
                )
                + score
            )


            if section not in section_data:

                section_data[
                    section
                ] = {
                    "section": section,
                    "dense_score": None,
                    "payload": {
                        "section": section
                    }
                }


        # =================================
        # 4. Sort fused candidates
        # =================================

        ranked_sections = sorted(
            fusion_scores.keys(),
            key=lambda section:
            fusion_scores[section],
            reverse=True
        )


        # =================================
        # 5. Build section-level candidates
        # =================================

        candidates = []


        for section in ranked_sections[:20]:

            parent_text = (
                self.get_section_text(
                    section
                )
            )


            original_payload = (
                section_data[
                    section
                ].get(
                    "payload",
                    {}
                )
            )


            payload = dict(
                original_payload
            )


            # IMPORTANT:
            # Replace child chunk with
            # parent section representation
            # for reranking.
            payload[
                "text"
            ] = parent_text


            candidates.append({
                "section": section,

                "fusion_score":
                    fusion_scores[
                        section
                    ],

                "payload":
                    payload
            })


        # =================================
        # 6. Cross-encoder reranking
        # =================================

        final_results = (
            self.reranker.rerank(
                query=query,
                candidates=candidates,
                limit=limit
            )
        )


        return final_results