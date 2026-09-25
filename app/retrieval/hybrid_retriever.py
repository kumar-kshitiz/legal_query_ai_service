import json
import re

from app.embeddings.embedder import LegalEmbedder

from app.vectorstore.qdrant_store import (
    LegalVectorStore
)

from app.retrieval.bm25_retriever import (
    BM25LegalRetriever
)

from app.retrieval.cross_encoder_reranker import (
    LegalCrossEncoderReranker
)


class HybridLegalRetriever:

    # --------------------------------------------------
    # If Rank #1 and Rank #2 are closer than this,
    # treat the result as ambiguous.
    #
    # We start conservatively so accuracy is protected.
    # --------------------------------------------------

    DISAMBIGUATION_GAP_THRESHOLD = 0.12


    def __init__(self):

        self.embedder = LegalEmbedder()

        self.vector_store = LegalVectorStore()

        self.bm25 = BM25LegalRetriever()

        self.reranker = (
            LegalCrossEncoderReranker()
        )


        # ==========================================
        # Load complete parent sections
        # ==========================================

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

            self.section_map[
                sec
            ] = section


    # ==============================================
    # Section helpers
    # ==============================================

    def get_section_text(
        self,
        section: str
    ) -> str:

        data = self.section_map.get(
            str(section)
        )


        if not data:

            return ""


        return data.get(
            "text",
            ""
        )


    def get_section_heading(
        self,
        section: str
    ) -> str:

        data = self.section_map.get(
            str(section)
        )


        if not data:

            return ""


        heading = data.get(
            "heading",
            ""
        )


        if heading:

            return heading.strip()


        text = data.get(
            "text",
            ""
        ).strip()


        if not text:

            return ""


        first_line = (
            text.splitlines()[0]
            .strip()
        )


        first_line = re.sub(
            r"^\s*\d+[A-Za-z]*"
            r"\s*[\.\-—:]*\s*",
            "",
            first_line
        )


        first_line = (
            first_line.replace(
                "—",
                " "
            )
        )


        first_line = re.sub(
            r"\s+",
            " ",
            first_line
        ).strip()


        return first_line[:250]


    def get_short_section_text(
        self,
        section: str
    ) -> str:

        heading = (
            self.get_section_heading(
                section
            )
        )


        text = (
            self.get_section_text(
                section
            )
        )


        short_text = (
            text[:700]
        )


        if heading:

            return (
                heading
                + ". "
                + short_text
            )


        return short_text


    def get_full_section_text(
        self,
        section: str
    ) -> str:

        heading = (
            self.get_section_heading(
                section
            )
        )


        text = (
            self.get_section_text(
                section
            )
        )


        text = text[:2000]


        if heading:

            return (
                heading
                + ". "
                + text
            )


        return text


    # ==============================================
    # Normalize scores inside Top-3
    # ==============================================

    def normalize_scores(
        self,
        score_map
    ):

        if not score_map:

            return {}


        values = list(
            score_map.values()
        )


        minimum = min(
            values
        )

        maximum = max(
            values
        )


        if abs(
            maximum - minimum
        ) < 1e-8:

            return {

                section: 0.5

                for section
                in score_map

            }


        return {

            section: (
                score - minimum
            )
            /
            (
                maximum - minimum
            )

            for section, score
            in score_map.items()

        }


    # ==============================================
    # Rerank one representation
    # ==============================================

    def rerank_view(
        self,
        query,
        candidates,
        view
    ):

        view_candidates = []


        for candidate in candidates:

            section = str(
                candidate[
                    "section"
                ]
            )


            payload = dict(
                candidate.get(
                    "payload",
                    {}
                )
            )


            if view == "heading":

                text = (

                    "Section "
                    + section
                    + ". "
                    + self.get_section_heading(
                        section
                    )

                )


            elif view == "short":

                text = (
                    self.get_short_section_text(
                        section
                    )
                )


            else:

                text = (
                    self.get_full_section_text(
                        section
                    )
                )


            payload[
                "text"
            ] = text


            view_candidates.append({

                "section":
                    section,

                "fusion_score":
                    candidate.get(
                        "fusion_score",
                        0
                    ),

                "payload":
                    payload
            })


        reranked = (

            self.reranker.rerank(

                query=query,

                candidates=view_candidates,

                limit=len(
                    view_candidates
                )
            )

        )


        scores = {}

        ranks = {}


        for rank, result in enumerate(
            reranked,
            start=1
        ):

            section = str(
                result[
                    "section"
                ]
            )


            scores[
                section
            ] = float(

                result.get(
                    "rerank_score",
                    0
                )

            )


            ranks[
                section
            ] = rank


        return scores, ranks


    # ==============================================
    # Determine whether query is ambiguous
    # ==============================================

    def needs_disambiguation(
        self,
        results
    ):

        if len(
            results
        ) < 2:

            return False, 1.0


        top1_score = float(

            results[0].get(
                "rerank_score",
                0
            )

        )


        top2_score = float(

            results[1].get(
                "rerank_score",
                0
            )

        )


        gap = abs(
            top1_score
            - top2_score
        )


        ambiguous = (

            gap
            <
            self.DISAMBIGUATION_GAP_THRESHOLD

        )


        return ambiguous, gap


    # ==============================================
    # Top-3 legal disambiguation
    # ==============================================

    def disambiguate_top3(
        self,
        query,
        initial_results
    ):

        if len(
            initial_results
        ) < 2:

            return initial_results


        top_candidates = (
            initial_results[:3]
        )


        remaining = (
            initial_results[3:]
        )


        # ==========================================
        # Original cross-encoder scores
        # ==========================================

        original_scores = {


            str(result["section"]):
            float(
                result.get(
                    "rerank_score",
                    0
                )
            )


            for result
            in top_candidates

        }


        original_ranks = {


            str(result["section"]):
            rank


            for rank, result
            in enumerate(
                top_candidates,
                start=1
            )

        }


        # ==========================================
        # Heading representation
        # ==========================================

        heading_scores, heading_ranks = (
            self.rerank_view(

                query,

                top_candidates,

                "heading"
            )
        )


        # ==========================================
        # Short provision representation
        # ==========================================

        short_scores, short_ranks = (
            self.rerank_view(

                query,

                top_candidates,

                "short"
            )
        )


        # ==========================================
        # Normalize
        # ==========================================

        original_norm = (
            self.normalize_scores(
                original_scores
            )
        )


        heading_norm = (
            self.normalize_scores(
                heading_scores
            )
        )


        short_norm = (
            self.normalize_scores(
                short_scores
            )
        )


        final_scores = {}


        # ==========================================
        # Combine evidence
        # ==========================================

        for candidate in top_candidates:

            section = str(
                candidate[
                    "section"
                ]
            )


            score_component = (

                0.50
                *
                original_norm.get(
                    section,
                    0
                )

                +

                0.30
                *
                short_norm.get(
                    section,
                    0
                )

                +

                0.20
                *
                heading_norm.get(
                    section,
                    0
                )

            )


            original_rr = (

                1.0

                /

                original_ranks.get(
                    section,
                    3
                )

            )


            short_rr = (

                1.0

                /

                short_ranks.get(
                    section,
                    3
                )

            )


            heading_rr = (

                1.0

                /

                heading_ranks.get(
                    section,
                    3
                )

            )


            agreement_score = (

                original_rr
                +
                short_rr
                +
                heading_rr

            ) / 3.0


            final_score = (

                0.80
                *
                score_component

                +

                0.20
                *
                agreement_score

            )


            final_scores[
                section
            ] = final_score


        # ==========================================
        # Conservative promotion
        # ==========================================

        original_top1 = str(

            top_candidates[
                0
            ][
                "section"
            ]

        )


        best_section = max(

            final_scores,

            key=final_scores.get

        )


        original_top1_score = (

            final_scores[
                original_top1
            ]

        )


        best_score = (

            final_scores[
                best_section
            ]

        )


        promotion_margin = 0.06


        if (

            best_section
            != original_top1

            and

            (
                best_score
                -
                original_top1_score
            )
            <
            promotion_margin

        ):

            best_section = (
                original_top1
            )


        # ==========================================
        # Reorder only Top-3
        # ==========================================

        reordered = sorted(

            top_candidates,

            key=lambda result: (

                1
                if str(
                    result[
                        "section"
                    ]
                )
                == best_section
                else 0,

                final_scores.get(
                    str(
                        result[
                            "section"
                        ]
                    ),
                    0
                )

            ),

            reverse=True
        )


        # ==========================================
        # Diagnostics
        # ==========================================

        for result in reordered:

            section = str(
                result[
                    "section"
                ]
            )


            result[
                "original_rank"
            ] = original_ranks.get(
                section
            )


            result[
                "original_rerank_score"
            ] = original_scores.get(
                section,
                0
            )


            result[
                "heading_score"
            ] = heading_scores.get(
                section,
                0
            )


            result[
                "short_score"
            ] = short_scores.get(
                section,
                0
            )


            result[
                "disambiguation_score"
            ] = final_scores.get(
                section,
                0
            )


            result[
                "disambiguation_applied"
            ] = True


        return (
            reordered
            +
            remaining
        )


    # ==============================================
    # Main search
    # ==============================================

    def search(
        self,
        query: str,
        limit: int = 5,
        disambiguate: bool = True,
        force_disambiguation: bool = False
    ):

        # ==========================================
        # 1. Dense retrieval
        # ==========================================

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


        for rank, result in enumerate(
            dense_results,
            start=1
        ):

            section = str(

                result.payload.get(
                    "section"
                )

            )


            if section in seen:

                continue


            seen.add(
                section
            )


            dense_sections.append({

                "section":
                    section,

                "dense_score":
                    float(
                        result.score
                    ),

                "dense_rank":
                    rank,

                "payload":
                    result.payload
            })


        # ==========================================
        # 2. BM25
        # ==========================================

        bm25_results = (

            self.bm25.search(

                query,

                limit=20
            )

        )


        # ==========================================
        # 3. RRF
        # ==========================================

        fusion_scores = {}

        section_data = {}


        k = 60

        dense_weight = 1.0

        bm25_weight = 0.6


        for rank, result in enumerate(
            dense_sections,
            start=1
        ):

            section = (
                result[
                    "section"
                ]
            )


            score = (

                dense_weight

                /

                (
                    k
                    +
                    rank
                )

            )


            fusion_scores[
                section
            ] = (

                fusion_scores.get(
                    section,
                    0
                )

                +
                score

            )


            section_data[
                section
            ] = result


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

                (
                    k
                    +
                    rank
                )

            )


            fusion_scores[
                section
            ] = (

                fusion_scores.get(
                    section,
                    0
                )

                +
                score

            )


            if section not in section_data:

                section_data[
                    section
                ] = {

                    "section":
                        section,

                    "dense_score":
                        None,

                    "dense_rank":
                        None,

                    "payload": {

                        "section":
                            section

                    }
                }


            section_data[
                section
            ][
                "bm25_rank"
            ] = rank


        # ==========================================
        # 4. Sort candidates
        # ==========================================

        ranked_sections = sorted(

            fusion_scores.keys(),

            key=lambda section:

            fusion_scores[
                section
            ],

            reverse=True
        )


        # ==========================================
        # 5. Build parent-section candidates
        # ==========================================

        candidates = []


        for section in ranked_sections[
            :20
        ]:

            parent_text = (

                self.get_full_section_text(
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


            payload[
                "text"
            ] = parent_text


            candidates.append({

                "section":
                    section,

                "fusion_score":
                    fusion_scores[
                        section
                    ],

                "payload":
                    payload
            })


        # ==========================================
        # 6. Main cross-encoder
        # ==========================================

        base_limit = max(
            limit,
            5
        )


        final_results = (

            self.reranker.rerank(

                query=query,

                candidates=candidates,

                limit=base_limit
            )

        )


        # ==========================================
        # Store original ranking before any changes
        # ==========================================

        for rank, result in enumerate(
            final_results,
            start=1
        ):

            result[
                "original_rank"
            ] = rank


            result[
                "original_rerank_score"
            ] = float(

                result.get(
                    "rerank_score",
                    0
                )

            )


            result[
                "disambiguation_applied"
            ] = False


        # ==========================================
        # 7. Check ambiguity
        # ==========================================

        ambiguous, score_gap = (
            self.needs_disambiguation(
                final_results
            )
        )


        # Add gap information to all results
        for result in final_results:

            result[
                "top12_score_gap"
            ] = score_gap


            result[
                "ambiguous"
            ] = ambiguous


        # ==========================================
        # 8. Conditional Top-3 disambiguation
        # ==========================================

        should_disambiguate = (

            disambiguate

            and

            (
                ambiguous
                or
                force_disambiguation
            )

        )


        if should_disambiguate:

            final_results = (

                self.disambiguate_top3(

                    query,

                    final_results
                )

            )


            for result in final_results:

                result[
                    "top12_score_gap"
                ] = score_gap


                result[
                    "ambiguous"
                ] = ambiguous


        return final_results[
            :limit
        ]