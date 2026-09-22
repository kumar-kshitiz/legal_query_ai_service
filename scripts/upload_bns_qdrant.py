import json
import uuid
import numpy as np

from qdrant_client.models import PointStruct

from app.vectorstore.qdrant_store import (
    LegalVectorStore
)


chunks_path = (
    "data/acts/bns_2023_v1_chunks.json"
)

embeddings_path = (
    "data/acts/bns_2023_v1_embeddings.npy"
)

metadata_path = (
    "data/acts/bns_2023_v1.json"
)


# -----------------------------
# Load chunks
# -----------------------------

with open(
    chunks_path,
    "r",
    encoding="utf-8"
) as f:

    chunks = json.load(f)


# -----------------------------
# Load embeddings
# -----------------------------

embeddings = np.load(
    embeddings_path
)


# -----------------------------
# Load document metadata
# -----------------------------

with open(
    metadata_path,
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)


print("Chunks:", len(chunks))
print("Embeddings:", len(embeddings))


if len(chunks) != len(embeddings):

    raise ValueError(
        "Chunk and embedding counts do not match."
    )


# -----------------------------
# Initialize Qdrant
# -----------------------------

store = LegalVectorStore()

store.create_collection()


# -----------------------------
# Build Qdrant points
# -----------------------------

points = []


for i, chunk in enumerate(chunks):

    # Qdrant accepts UUID IDs.
    # This gives each chunk a stable ID.
    point_id = str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            chunk["chunk_id"]
        )
    )


    payload = {

        "chunk_id":
            chunk["chunk_id"],

        "document_id":
            chunk["document_id"],

        "law_id":
            metadata.get("law_id"),

        "document_type":
            metadata.get("document_type"),

        "title":
            metadata.get("title"),

        "act_name":
            chunk["act_name"],

        "act_number":
            metadata.get("act_number"),

        "section":
            chunk["section"],

        "chapter":
            chunk["chapter"],

        "chunk_index":
            chunk["chunk_index"],

        "text":
            chunk["text"],

        "jurisdiction":
            metadata.get("jurisdiction"),

        "version":
            metadata.get("version"),

        "status":
            metadata.get("status"),

        "source_type":
            metadata.get("source_type"),

        "source_url":
            metadata.get("source_url"),

        "content_hash":
            metadata.get("content_hash"),

        "verified":
            metadata.get("verified"),

        "human_reviewed":
            metadata.get(
                "human_reviewed"
            )
    }


    point = PointStruct(

        id=point_id,

        vector=embeddings[i].tolist(),

        payload=payload
    )


    points.append(point)


# -----------------------------
# Upload
# -----------------------------

print("\nUploading points...")


store.upload_points(
    points
)


print("\nUpload complete.")


print(
    "Points in Qdrant:",
    store.count()
)