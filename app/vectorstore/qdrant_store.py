from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)


COLLECTION_NAME = "legal_documents"

VECTOR_SIZE = 384


class LegalVectorStore:

    def __init__(self):

        self.client = QdrantClient(
            url="http://localhost:6333"
        )


    def create_collection(self):

        exists = self.client.collection_exists(
            COLLECTION_NAME
        )

        if exists:
            print(
                f"Collection '{COLLECTION_NAME}' already exists."
            )

            return

        self.client.create_collection(

            collection_name=COLLECTION_NAME,

            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )

        print(
            f"Collection '{COLLECTION_NAME}' created."
        )


    def upload_points(
        self,
        points: list[PointStruct]
    ):

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True
        )


    def count(self):

        result = self.client.count(
            collection_name=COLLECTION_NAME,
            exact=True
        )

        return result.count

    
    def search(
        self,
        query_vector,
        limit: int = 5
    ):

        result = self.client.query_points(

            collection_name=COLLECTION_NAME,

            query=query_vector.tolist(),

            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="status",
                        match=MatchValue(
                            value="active"
                        )
                    ),

                    FieldCondition(
                        key="verified",
                        match=MatchValue(
                            value=True
                        )
                    )
                ]
            ),

            limit=limit,

            with_payload=True
        )

        return result.points