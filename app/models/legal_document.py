from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class Jurisdiction(BaseModel):
    country: str = "India"
    state: Optional[str] = None


class LegalDocument(BaseModel):
    document_id: str

    document_type: str
    title: str

    legal_topic: list[str] = []

    jurisdiction: Jurisdiction = Jurisdiction()

    act_name: Optional[str] = None
    act_number: Optional[str] = None

    chapter: Optional[str] = None
    section: Optional[str] = None
    subsection: Optional[str] = None

    court: Optional[str] = None
    case_number: Optional[str] = None

    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    version: str = "current"

    verified: bool = False
    verified_by: Optional[str] = None

    source_type: str
    source_url: Optional[str] = None

    text: str

    ingested_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class LegalChunk(BaseModel):
    chunk_id: str
    document_id: str

    text: str

    document_type: str
    title: str

    legal_topic: list[str] = []

    jurisdiction: Jurisdiction

    act_name: Optional[str] = None

    chapter: Optional[str] = None
    section: Optional[str] = None
    subsection: Optional[str] = None

    court: Optional[str] = None

    source_url: Optional[str] = None

    verified: bool = False

    chunk_index: int