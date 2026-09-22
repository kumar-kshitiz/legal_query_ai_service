from fastapi import FastAPI

from app.models.legal_document import (
    LegalDocument,
    Jurisdiction
)


app = FastAPI(
    title="Legal Query AI Service",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Legal Query AI Service is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/test-document")
def test_document():

    doc = LegalDocument(
        document_id="bns_2023_103",

        document_type="statute",

        title="Bharatiya Nyaya Sanhita, 2023",

        legal_topic=[
            "criminal_law",
            "murder"
        ],

        jurisdiction=Jurisdiction(
            country="India"
        ),

        act_name="Bharatiya Nyaya Sanhita, 2023",

        section="103",

        source_type="official",

        text="Test legal document content.",

        verified=True,

        verified_by="MNLU"
    )

    return doc