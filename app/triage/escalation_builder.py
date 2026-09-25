from datetime import (
    datetime,
    timezone,
)

from typing import Any


class EscalationBuilder:

    def build(
        self,
        query: str,
        stage: str,
        triage: Any,
        retrieval_results: list[dict] | None = None,
        rag_reason: str | None = None,
    ) -> dict:

        retrieval_results = (
            retrieval_results
            or []
        )


        # ==========================================
        # Retrieved provisions
        # ==========================================

        provisions = []


        for rank, result in enumerate(
            retrieval_results,
            start=1
        ):

            payload = result.get(
                "payload",
                {}
            )


            source = result.get(
                "legal_source",
                {}
            )


            provisions.append({

                "rank":
                    rank,

                "section":
                    str(
                        result.get(
                            "section"
                        )
                    ),

                "text":
                    payload.get(
                        "text",
                        ""
                    ),

                "rerank_score":
                    float(
                        result.get(
                            "rerank_score",
                            0
                        )
                    ),

                "source": {

                    "document_id":
                        source.get(
                            "document_id"
                        ),

                    "law_id":
                        source.get(
                            "law_id"
                        ),

                    "version":
                        source.get(
                            "version"
                        ),

                    "source_url":
                        source.get(
                            "source_url"
                        ),

                    "verified":
                        source.get(
                            "verified"
                        ),

                    "last_checked_at":
                        source.get(
                            "last_checked_at"
                        ),
                }
            })


        # ==========================================
        # Priority
        # ==========================================

        priority = (
            self.determine_priority(
                triage
            )
        )


        # ==========================================
        # Human-readable category
        # ==========================================

        category = (
            self.determine_category(
                triage
            )
        )


        # ==========================================
        # Payload
        # ==========================================

        return {

            "type":
                "legal_query_escalation",

            "status":
                "pending",

            "priority":
                priority,

            "category":
                category,

            "query":
                query,

            "routing_stage":
                stage,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "triage": {

                "confidence":
                    triage.confidence,

                "sensitive":
                    triage.sensitive,

                "urgent":
                    triage.urgent,

                "ambiguous":
                    triage.ambiguous,

                "complex":
                    triage.complex,

                "reasons":
                    triage.reasons,
            },

            "rag_reason":
                rag_reason,

            "retrieved_provisions":
                provisions,

            "assignment": {

                "assigned_to":
                    None,

                "assigned_at":
                    None,
            },

            "resolution": {

                "resolved":
                    False,

                "resolved_by":
                    None,

                "resolved_at":
                    None,

                "response":
                    None,
            }
        }


    # ==============================================
    # Priority
    # ==============================================

    def determine_priority(
        self,
        triage: Any
    ) -> str:

        if triage.urgent:

            return "critical"


        if triage.sensitive:

            return "high"


        if triage.complex:

            return "medium"


        if triage.ambiguous:

            return "medium"


        if triage.confidence == "low":

            return "medium"


        return "normal"


    # ==============================================
    # Category
    # ==============================================

    def determine_category(
        self,
        triage: Any
    ) -> str:

        if triage.urgent:

            return "urgent"


        if triage.sensitive:

            return "sensitive"


        if triage.complex:

            return "complex"


        if triage.ambiguous:

            return "ambiguous"


        if triage.confidence == "low":

            return "low_confidence"


        return "manual_review"