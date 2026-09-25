from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
)

from pydantic import BaseModel

from app.retrieval.safe_hybrid_retriever import (
    SafeHybridLegalRetriever,
    LegalKnowledgeUnavailableError,
)


# ==================================================
# Global retriever
# ==================================================

retriever = None


# ==================================================
# App lifespan
#
# Loads embedding model + cross encoder only once.
# ==================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    global retriever


    print(
        "\n===================================="
    )

    print(
        "LOADING LEGAL RETRIEVAL SYSTEM"
    )

    print(
        "===================================="
    )


    retriever = (
        SafeHybridLegalRetriever()
    )


    print(
        "\n✅ Legal retrieval system ready."
    )


    yield


    print(
        "\nShutting down legal service."
    )


# ==================================================
# FastAPI app
# ==================================================

app = FastAPI(

    title="Legal Intelligence Service",

    version="1.0.0",

    lifespan=lifespan,
)


# ==================================================
# Request model
# ==================================================

class SearchRequest(
    BaseModel
):

    query: str

    limit: int = 5


# ==================================================
# Root
# ==================================================

@app.get("/")
def root():

    return {

        "service":
            "Legal Intelligence Service",

        "status":
            "running"
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
            retriever is not None
    }


# ==================================================
# Search
# ==================================================

@app.post("/search")
def search(
    request: SearchRequest
):

    if retriever is None:

        raise HTTPException(

            status_code=503,

            detail=(
                "Legal retrieval system "
                "is not ready."
            )
        )


    query = (
        request.query.strip()
    )


    if not query:

        raise HTTPException(

            status_code=400,

            detail=(
                "Query cannot be empty."
            )
        )


    limit = max(
        1,
        min(
            request.limit,
            10
        )
    )


    try:

        results = (
            retriever.search(

                query,

                limit=limit
            )
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


    response_results = []


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


        response_results.append({

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


    return {

        "query":
            query,

        "count":
            len(
                response_results
            ),

        "results":
            response_results
    }