from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import ScoredPoint


class VectorDatabase:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.client = AsyncQdrantClient(host=host, port=port)

    async def create_collection(self, collection_name: str, vector_size: int):
        if not await self.client.collection_exists(collection_name=collection_name):
            vectors_config = models.VectorParams(
                size=vector_size, distance=models.Distance.COSINE
            )
            await self.client.create_collection(
                collection_name=collection_name, vectors_config=vectors_config
            )

    async def insert(
        self,
        collection_name: str,
        embedding_vector: list[float],
        original_text: str,
        source: str,
    ) -> None:
        response = await self.client.count(collection_name=collection_name)
        await self.client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=response.count,
                    vector=embedding_vector,
                    payload={
                        "source": source,
                        "original_text": original_text,
                    },
                )
            ],
        )

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        retrieval_limit: int,
        score_threshold: float,
    ) -> list[ScoredPoint]:
        response = await self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=retrieval_limit,
            score_threshold=score_threshold,
            with_vectors=True
        )
        return response.points

    async def delete_collection(self, name: str) -> bool:
        return await self.client.delete_collection(collection_name=name)
