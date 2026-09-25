import re

from dataclasses import (
    dataclass,
    field,
)

from enum import Enum


# ==================================================
# Routing decisions
# ==================================================

class QueryRoute(
    str,
    Enum
):

    AI = "ai"

    HUMAN = "human"


# ==================================================
# Triage result
# ==================================================

@dataclass
class TriageResult:

    route: QueryRoute

    reasons: list[str] = field(
        default_factory=list
    )

    sensitive: bool = False

    ambiguous: bool = False

    complex: bool = False

    urgent: bool = False

    confidence: str = "unknown"


# ==================================================
# Query triage engine
# ==================================================

class LegalQueryTriage:

    def __init__(self):

        # ==========================================
        # Sensitive matters
        # ==========================================

        self.sensitive_patterns = [

            r"\brape\b",

            r"\bsexual assault\b",

            r"\bsexual harassment\b",

            r"\bmolestation\b",

            r"\bminor\b",

            r"\bchild abuse\b",

            r"\bdomestic violence\b",

            r"\bsuicide\b",

            r"\bself[\s-]?harm\b",

            r"\bterrorism\b",

            r"\bkidnap",

            r"\bhuman trafficking\b",

            r"\bblackmail\b",

            r"\bextortion\b",
        ]


        # ==========================================
        # Urgent matters
        # ==========================================

        self.urgent_patterns = [

            r"\bright now\b",

            r"\bimmediately\b",

            r"\burgent\b",

            r"\bin danger\b",

            r"\bgoing to kill\b",

            r"\bthreatening to kill\b",

            r"\bbeing attacked\b",

            r"\bcurrently attacking\b",

            r"\bpolice arrested me\b",

            r"\bin police custody\b",
        ]


        # ==========================================
        # Event connectors
        # ==========================================

        self.event_connectors = [

            "then",

            "later",

            "after that",

            "before that",

            "afterwards",

            "meanwhile",

            "subsequently",

            "also",

            "additionally",

            "furthermore",

            "however",

            "although",

            "whereas",
        ]


        # ==========================================
        # Multiple-action indicators
        # ==========================================

        self.action_patterns = [

            r"\bthreaten",

            r"\btook\b",

            r"\bstole\b",

            r"\bhit\b",

            r"\bassault",

            r"\bkill",

            r"\battack",

            r"\bhide\b",

            r"\bhelped\b",

            r"\bforced\b",

            r"\bdeceived\b",

            r"\bcheat",

            r"\bblackmail",

            r"\bextort",

            r"\bdamage",

            r"\bentered\b",

            r"\btrespass",
        ]


    # ==================================================
    # Pattern matching
    # ==================================================

    def matches_any(
        self,
        text: str,
        patterns: list[str]
    ) -> bool:

        return any(

            re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for pattern
            in patterns
        )


    # ==================================================
    # Complexity detection
    # ==================================================

    def detect_complexity(
        self,
        query: str
    ) -> bool:

        lower_query = (
            query.lower()
        )


        words = (
            query.split()
        )


        if len(words) > 100:

            return True


        connector_count = sum(

            1

            for connector
            in self.event_connectors

            if connector
            in lower_query
        )


        if connector_count >= 2:

            return True


        action_count = sum(

            1

            for pattern
            in self.action_patterns

            if re.search(
                pattern,
                lower_query
            )
        )


        if action_count >= 3:

            return True


        if query.count("?") >= 2:

            return True


        return False


    # ==================================================
    # Ambiguity detection
    # ==================================================

    def detect_ambiguity(
        self,
        query: str
    ) -> bool:

        cleaned = (
            query.strip()
        )


        if len(
            cleaned.split()
        ) < 4:

            return True


        vague_queries = {

            "what should i do",

            "is this illegal",

            "is this legal",

            "help me legally",

            "what law applies",

            "can they do this",
        }


        normalized = (

            cleaned
            .lower()
            .rstrip("?")
            .strip()

        )


        if normalized in vague_queries:

            return True


        return False


    # ==================================================
    # Retrieval confidence
    # ==================================================

    def evaluate_retrieval_confidence(
        self,
        results: list[dict]
    ) -> str:

        if not results:

            return "low"


        if len(results) == 1:

            return "medium"


        first = results[0]

        second = results[1]


        # ==========================================
        # Case 1:
        # Legal disambiguation was applied.
        #
        # Use the final disambiguation evidence
        # rather than only raw cross-encoder scores.
        # ==========================================

        disambiguation_applied = bool(

            first.get(
                "disambiguation_applied",
                False
            )

        )


        first_disambiguation_score = (
            first.get(
                "disambiguation_score"
            )
        )


        second_disambiguation_score = (
            second.get(
                "disambiguation_score"
            )
        )


        if (

            disambiguation_applied

            and

            first_disambiguation_score
            is not None

            and

            second_disambiguation_score
            is not None

        ):

            top1 = float(
                first_disambiguation_score
            )


            top2 = float(
                second_disambiguation_score
            )


            gap = (
                top1
                -
                top2
            )


            # Strong final separation
            if gap >= 0.12:

                return "high"


            # Reasonable final separation
            if gap >= 0.04:

                return "medium"


            return "low"


        # ==========================================
        # Case 2:
        # Normal cross-encoder ranking
        # ==========================================

        top1 = float(

            first.get(
                "rerank_score",
                0
            )

        )


        top2 = float(

            second.get(
                "rerank_score",
                0
            )

        )


        gap12 = (
            top1
            -
            top2
        )


        # ==========================================
        # Also consider Top-3 separation
        # ==========================================

        top3 = 0.0


        if len(results) >= 3:

            top3 = float(

                results[2].get(
                    "rerank_score",
                    0
                )

            )


        gap13 = (
            top1
            -
            top3
        )


        # ==========================================
        # Strong evidence
        # ==========================================

        if (

            top1 >= 0.85

            and

            (
                gap12 >= 0.07
                or
                gap13 >= 0.25
            )

        ):

            return "high"


        # ==========================================
        # Moderate evidence
        # ==========================================

        if (

            top1 >= 0.45

            and

            (
                gap12 >= 0.02
                or
                gap13 >= 0.10
            )

        ):

            return "medium"


        return "low"


    # ==================================================
    # Main classification
    # ==================================================

    def classify(
        self,
        query: str,
        retrieval_results: list[dict] | None = None
    ) -> TriageResult:

        query = (
            query.strip()
        )


        reasons = []


        # ==========================================
        # Empty query
        # ==========================================

        if not query:

            return TriageResult(

                route=QueryRoute.HUMAN,

                reasons=[
                    "Query is empty."
                ],

                ambiguous=True,

                confidence="low"
            )


        # ==========================================
        # Sensitive
        # ==========================================

        sensitive = (
            self.matches_any(

                query,

                self.sensitive_patterns
            )
        )


        if sensitive:

            reasons.append(
                "Sensitive legal matter detected."
            )


        # ==========================================
        # Urgent
        # ==========================================

        urgent = (
            self.matches_any(

                query,

                self.urgent_patterns
            )
        )


        if urgent:

            reasons.append(
                "Urgent or immediate-risk situation detected."
            )


        # ==========================================
        # Ambiguous
        # ==========================================

        ambiguous = (
            self.detect_ambiguity(
                query
            )
        )


        if ambiguous:

            reasons.append(
                "Query does not contain enough legal context."
            )


        # ==========================================
        # Complex
        # ==========================================

        complex_query = (
            self.detect_complexity(
                query
            )
        )


        if complex_query:

            reasons.append(
                "Query contains multiple or complex factual issues."
            )


        # ==========================================
        # Retrieval confidence
        # ==========================================

        confidence = "unknown"


        if retrieval_results is not None:

            confidence = (
                self.evaluate_retrieval_confidence(
                    retrieval_results
                )
            )


            if confidence == "low":

                reasons.append(
                    "Retrieval confidence is low."
                )


        # ==========================================
        # Escalation
        # ==========================================

        should_escalate = any([

            sensitive,

            urgent,

            ambiguous,

            complex_query,

            confidence == "low",
        ])


        if should_escalate:

            return TriageResult(

                route=QueryRoute.HUMAN,

                reasons=reasons,

                sensitive=sensitive,

                ambiguous=ambiguous,

                complex=complex_query,

                urgent=urgent,

                confidence=confidence
            )


        # ==========================================
        # AI route
        # ==========================================

        if not reasons:

            reasons.append(
                "Query passed deterministic triage checks."
            )


        return TriageResult(

            route=QueryRoute.AI,

            reasons=reasons,

            sensitive=sensitive,

            ambiguous=ambiguous,

            complex=complex_query,

            urgent=urgent,

            confidence=confidence
        )