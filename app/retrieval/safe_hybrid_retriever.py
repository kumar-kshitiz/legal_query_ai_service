import json

from pathlib import Path

from app.retrieval.hybrid_retriever import (
    HybridLegalRetriever
)

from app.safety.legal_freshness import (
    LegalFreshnessChecker
)


class LegalKnowledgeUnavailableError(
    RuntimeError
):
    pass


class SafeHybridLegalRetriever:

    def __init__(self):

        self.metadata_path = Path(
            "data/acts/"
            "bns_2023_v1.json"
        )


        # ------------------------------------------
        # Keep your existing 100/100/100 retriever
        # completely unchanged.
        # ------------------------------------------

        self.retriever = (
            HybridLegalRetriever()
        )


    # ==============================================
    # Load latest metadata every search
    #
    # Metadata is tiny, so this is cheap.
    # It also means freshness changes are picked up
    # without restarting FastAPI.
    # ==============================================

    def load_metadata(
        self
    ) -> dict:

        if not self.metadata_path.exists():

            raise (
                LegalKnowledgeUnavailableError(
                    "Legal metadata file is missing."
                )
            )


        with open(
            self.metadata_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)


    # ==============================================
    # Verify legal source can be used
    # ==============================================

    def check_eligibility(
        self
    ) -> dict:

        metadata = (
            self.load_metadata()
        )


        checker = (
            LegalFreshnessChecker()
        )


        result = checker.validate(
            metadata
        )


        return result


    # ==============================================
    # Search
    # ==============================================

    def search(
        self,
        query: str,
        limit: int = 5
    ):

        eligibility = (
            self.check_eligibility()
        )


        # ------------------------------------------
        # FAIL CLOSED
        #
        # Never silently use stale / superseded /
        # unverified legal material.
        # ------------------------------------------

        if not eligibility[
            "eligible_for_retrieval"
        ]:

            failed_checks = []


            for name, check in (
                eligibility[
                    "checks"
                ].items()
            ):

                if not check[
                    "passed"
                ]:

                    failed_checks.append(
                        (
                            f"{name}: "
                            f"{check['message']}"
                        )
                    )


            reason = "; ".join(
                failed_checks
            )


            raise (
                LegalKnowledgeUnavailableError(
                    "Legal knowledge source is "
                    "not safe for retrieval. "
                    + reason
                )
            )


        # ------------------------------------------
        # Safe → use existing retrieval pipeline
        # ------------------------------------------

        results = (
            self.retriever.search(
                query,
                limit=limit
            )
        )


        # ------------------------------------------
        # Add version/source metadata to results
        #
        # Useful later for RAG citations.
        # ------------------------------------------

        metadata = (
            self.load_metadata()
        )


        for result in results:

            result[
                "legal_source"
            ] = {

                "document_id":
                    metadata.get(
                        "document_id"
                    ),

                "law_id":
                    metadata.get(
                        "law_id"
                    ),

                "version":
                    metadata.get(
                        "version"
                    ),

                "source_url":
                    metadata.get(
                        "source_url"
                    ),

                "last_checked_at":
                    metadata.get(
                        "last_checked_at"
                    ),

                "verified":
                    metadata.get(
                        "verified"
                    ),

                "effective_from":
                    metadata.get(
                        "effective_from"
                    ),

                "effective_to":
                    metadata.get(
                        "effective_to"
                    ),
            }


        return results