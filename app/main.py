from contextlib import asynccontextmanager

from threading import Lock

from fastapi import (
    FastAPI,
    HTTPException,
)

from pydantic import BaseModel

from app.retrieval.safe_hybrid_retriever import (
    SafeHybridLegalRetriever,
    LegalKnowledgeUnavailableError,
)

from app.triage.query_triage import (
    LegalQueryTriage,
    QueryRoute,
)

from app.triage.escalation_builder import (
    EscalationBuilder,
)

from app.rag.legal_answer_generator import (
    LegalAnswerGenerator,
)


# ==================================================
# Global components
# ==================================================

retriever = None

triage_engine = None

escalation_builder = None

answer_generator = None

generator_lock = Lock()


# ==================================================
# Lazy-load RAG model
# ==================================================

def get_answer_generator():

    global answer_generator


    if answer_generator is None:

        with generator_lock:

            if answer_generator is None:

                print(
                    "\n===================================="
                )

                print(
                    "LOADING LEGAL ANSWER MODEL"
                )

                print(
                    "===================================="
                )


                answer_generator = (
                    LegalAnswerGenerator()
                )


    return answer_generator


# ==================================================
# Lifespan
# ==================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    global retriever
    global triage_engine
    global escalation_builder


    print(
        "\n===================================="
    )

    print(
        "LOADING LEGAL INTELLIGENCE SERVICE"
    )

    print(
        "===================================="
    )


    retriever = (
        SafeHybridLegalRetriever()
    )


    triage_engine = (
        LegalQueryTriage()
    )


    escalation_builder = (
        EscalationBuilder()
    )


    print(
        "\n✅ Retrieval system ready."
    )

    print(
        "✅ Triage engine ready."
    )

    print(
        "✅ Escalation builder ready."
    )

    print(
        "ℹ️ RAG model will load lazily."
    )


    yield


    print(
        "\nShutting down legal service."
    )


# ==================================================
# FastAPI
# ==================================================

app = FastAPI(

    title="Legal Intelligence Service",

    version="2.2.0",

    lifespan=lifespan,
)


# ==================================================
# Request models
# ==================================================

class SearchRequest(
    BaseModel
):

    query: str

    limit: int = 5


class AnalyzeRequest(
    BaseModel
):

    query: str

    limit: int = 5


class ResolveRequest(
    BaseModel
):

    query: str

    limit: int = 3


# ==================================================
# Helpers
# ==================================================

def validate_query(
    query: str
) -> str:

    query = query.strip()


    if not query:

        raise HTTPException(

            status_code=400,

            detail="Query cannot be empty."
        )


    return query


def normalize_limit(
    limit: int
) -> int:

    return max(
        1,
        min(
            limit,
            10
        )
    )


def serialize_triage(
    decision
):

    return {

        "route":
            decision.route.value,

        "confidence":
            decision.confidence,

        "sensitive":
            decision.sensitive,

        "urgent":
            decision.urgent,

        "ambiguous":
            decision.ambiguous,

        "complex":
            decision.complex,

        "reasons":
            decision.reasons,
    }


def serialize_results(
    results
):

    output = []


    for rank, result in enumerate(
        results,
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


        output.append({

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

            "disambiguation_applied":
                bool(
                    result.get(
                        "disambiguation_applied",
                        False
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

                "effective_from":
                    source.get(
                        "effective_from"
                    ),

                "effective_to":
                    source.get(
                        "effective_to"
                    ),
            }
        })


    return output


# ==================================================
# Root
# ==================================================

@app.get("/")
def root():

    return {

        "service":
            "Legal Intelligence Service",

        "version":
            "2.2.0",

        "status":
            "running",
    }


# ==================================================
# Health
# ==================================================

@app.get("/health")
def health():

    return {

        "status":
            "ready",

        "retriever_loaded":
            retriever is not None,

        "triage_loaded":
            triage_engine is not None,

        "escalation_builder_loaded":
            escalation_builder is not None,

        "rag_loaded":
            answer_generator is not None,
    }


# ==================================================
# Search
# ==================================================

@app.post("/search")
def search(
    request: SearchRequest
):

    query = validate_query(
        request.query
    )


    limit = normalize_limit(
        request.limit
    )


    try:

        results = retriever.search(
            query,
            limit=limit
        )


    except LegalKnowledgeUnavailableError as e:

        raise HTTPException(

            status_code=503,

            detail={
                "error":
                    "legal_source_unavailable",

                "message":
                    str(e)
            }
        )


    return {

        "query":
            query,

        "count":
            len(results),

        "results":
            serialize_results(
                results
            ),
    }


# ==================================================
# Analyze
# ==================================================

@app.post("/analyze")
def analyze(
    request: AnalyzeRequest
):

    query = validate_query(
        request.query
    )


    limit = normalize_limit(
        request.limit
    )


    pre = triage_engine.classify(

        query,

        retrieval_results=None
    )


    if pre.route == QueryRoute.HUMAN:

        return {

            "query":
                query,

            "route":
                "human",

            "retrieval_performed":
                False,

            "triage":
                serialize_triage(
                    pre
                ),

            "results":
                [],
        }


    try:

        results = retriever.search(

            query,

            limit=limit
        )


    except LegalKnowledgeUnavailableError as e:

        raise HTTPException(

            status_code=503,

            detail={
                "error":
                    "legal_source_unavailable",

                "message":
                    str(e)
            }
        )


    final = triage_engine.classify(

        query,

        retrieval_results=results
    )


    return {

        "query":
            query,

        "route":
            final.route.value,

        "retrieval_performed":
            True,

        "triage":
            serialize_triage(
                final
            ),

        "results":
            serialize_results(
                results
            ),
    }


# ==================================================
# Resolve
# ==================================================

@app.post("/resolve")
def resolve(
    request: ResolveRequest
):

    query = validate_query(
        request.query
    )


    limit = normalize_limit(
        request.limit
    )


    # ==============================================
    # 1. PRE-TRIAGE
    # ==============================================

    pre_triage = triage_engine.classify(

        query,

        retrieval_results=None
    )


    if pre_triage.route == QueryRoute.HUMAN:

        escalation = (
            escalation_builder.build(

                query=query,

                stage="pre_triage",

                triage=pre_triage,

                retrieval_results=[]
            )
        )


        return {

            "query":
                query,

            "route":
                "human",

            "stage":
                "pre_triage",

            "retrieval_performed":
                False,

            "answer_generated":
                False,

            "triage":
                serialize_triage(
                    pre_triage
                ),

            "answer":
                None,

            "citations":
                [],

            "results":
                [],

            "escalation":
                escalation,

            "action":
                (
                    "Forward escalation payload "
                    "to Node.js/MongoDB."
                )
        }


    # ==============================================
    # 2. RETRIEVAL
    # ==============================================

    try:

        results = retriever.search(

            query,

            limit=limit
        )


    except LegalKnowledgeUnavailableError as e:

        raise HTTPException(

            status_code=503,

            detail={
                "error":
                    "legal_source_unavailable",

                "message":
                    str(e)
            }
        )


    # ==============================================
    # 3. RETRIEVAL-AWARE TRIAGE
    # ==============================================

    final_triage = triage_engine.classify(

        query,

        retrieval_results=results
    )


    serialized_results = (
        serialize_results(
            results
        )
    )


    if final_triage.route == QueryRoute.HUMAN:

        escalation = (
            escalation_builder.build(

                query=query,

                stage="retrieval_triage",

                triage=final_triage,

                retrieval_results=results
            )
        )


        return {

            "query":
                query,

            "route":
                "human",

            "stage":
                "retrieval_triage",

            "retrieval_performed":
                True,

            "answer_generated":
                False,

            "triage":
                serialize_triage(
                    final_triage
                ),

            "answer":
                None,

            "citations":
                [],

            "results":
                serialized_results,

            "escalation":
                escalation,

            "action":
                (
                    "Forward escalation payload "
                    "with retrieved provisions "
                    "to Node.js/MongoDB."
                )
        }


    # ==============================================
    # 4. GROUNDED RAG
    # ==============================================

    generator = (
        get_answer_generator()
    )


    generated = generator.generate(

        query,

        results
    )


    # ==============================================
    # 5. RAG ABSTENTION
    # ==============================================

    if generated.get(
        "needs_human_review",
        True
    ):

        escalation = (
            escalation_builder.build(

                query=query,

                stage="rag_abstention",

                triage=final_triage,

                retrieval_results=results,

                rag_reason=generated.get(
                    "reason"
                )
            )
        )


        return {

            "query":
                query,

            "route":
                "human",

            "stage":
                "rag_abstention",

            "retrieval_performed":
                True,

            "answer_generated":
                True,

            "triage":
                serialize_triage(
                    final_triage
                ),

            "answer":
                None,

            "citations":
                generated.get(
                    "cited_sections",
                    []
                ),

            "rag_reason":
                generated.get(
                    "reason"
                ),

            "results":
                serialized_results,

            "escalation":
                escalation,

            "action":
                (
                    "AI abstained. Forward "
                    "escalation payload to "
                    "Node.js/MongoDB."
                )
        }


    # ==============================================
    # 6. AI RESOLUTION
    # ==============================================

    return {

        "query":
            query,

        "route":
            "ai",

        "stage":
            "resolved",

        "retrieval_performed":
            True,

        "answer_generated":
            True,

        "triage":
            serialize_triage(
                final_triage
            ),

        "answer":
            generated.get(
                "answer"
            ),

        "citations":
            generated.get(
                "cited_sections",
                []
            ),

        "rag_reason":
            generated.get(
                "reason"
            ),

        "results":
            serialized_results,

        "escalation":
            None,

        "action":
            (
                "Return source-grounded "
                "answer to user."
            )
    }