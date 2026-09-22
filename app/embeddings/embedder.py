from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-en-v1.5"


class LegalEmbedder:

    def __init__(self):
        self.model = SentenceTransformer(
            MODEL_NAME
        )

    def embed_documents(
        self,
        texts: list[str]
    ):

        return self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True
        )
    
    
    def embed_query(
        self,
        query: str
    ):

        instruction = (
            "Represent this sentence for "
            "searching relevant passages: "
        )

        text = instruction + query

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding 