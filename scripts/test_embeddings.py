import json
import numpy as np

from app.embeddings.embedder import (
    LegalEmbedder
)


chunks_path = (
    "data/acts/"
    "bns_2023_v1_chunks.json"
)

embeddings_path = (
    "data/acts/"
    "bns_2023_v1_embeddings.npy"
)


with open(
    chunks_path,
    "r",
    encoding="utf-8"
) as f:

    chunks = json.load(f)


texts = [
    chunk["text"]
    for chunk in chunks
]


print("Chunks:", len(chunks))

print("\nLoading embedding model...")


embedder = LegalEmbedder()


print("\nGenerating embeddings...")


embeddings = embedder.embed_documents(
    texts
)


print("\n===== EMBEDDING VALIDATION =====")

print(
    "Embedding shape:",
    embeddings.shape
)

print(
    "Vector dimension:",
    embeddings.shape[1]
)

print(
    "First vector norm:",
    np.linalg.norm(
        embeddings[0]
    )
)

print(
    "Contains NaN:",
    np.isnan(
        embeddings
    ).any()
)


np.save(
    embeddings_path,
    embeddings
)


print(
    "\nSaved:",
    embeddings_path
)