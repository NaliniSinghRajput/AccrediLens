from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import get_settings


class VectorStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = QdrantClient(url=self.settings.qdrant_url)

    def ensure_collection(self, vector_size: int) -> None:
        collections = self.client.get_collections().collections
        existing = next((item for item in collections if item.name == self.settings.qdrant_collection), None)
        if existing:
            return
        self.client.create_collection(
            collection_name=self.settings.qdrant_collection,
            vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        )

    def upsert_chunks(self, points: list[tuple[str, list[float], dict]]) -> None:
        if not points:
            return
        self.ensure_collection(len(points[0][1]))
        self.client.upsert(
            collection_name=self.settings.qdrant_collection,
            points=[
                qmodels.PointStruct(id=point_id, vector=vector, payload=payload)
                for point_id, vector, payload in points
            ],
        )

    def search(self, paper_id: str, vector: list[float], limit: int) -> list[qmodels.ScoredPoint]:
        return self.client.search(
            collection_name=self.settings.qdrant_collection,
            query_vector=vector,
            query_filter=qmodels.Filter(
                must=[qmodels.FieldCondition(key="paper_id", match=qmodels.MatchValue(value=paper_id))]
            ),
            limit=limit,
            with_payload=True,
        )

    def delete_paper(self, paper_id: str) -> None:
        self.client.delete(
            collection_name=self.settings.qdrant_collection,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[qmodels.FieldCondition(key="paper_id", match=qmodels.MatchValue(value=paper_id))]
                )
            ),
        )
