import hashlib
import math
import os
import uuid
from collections.abc import Callable

from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


class PolicyMatch(BaseModel):
    has_sufficient_backing: bool
    best_score: float = Field(default=0.0)
    matched_policy: str | None = Field(default=None)


def default_local_embedder(text: str, dim: int = 64) -> list[float]:
    """Genera un embedding determinista ligero por tokens para validación local rápida."""
    vec = [0.0] * dim
    tokens = text.lower().split()
    if not tokens:
        return vec

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(dim):
            vec[i] += (digest[i % len(digest)] / 127.5) - 1.0

    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm > 0 else vec


class PolicyRAG:
    def __init__(
        self,
        collection_name: str = "policy_library",
        similarity_threshold: float = 0.65,
        vector_size: int = 64,
        client: QdrantClient | None = None,
        embedder: Callable[[str], list[float]] | None = None,
    ):
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.client = client or QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        self.vector_size = vector_size
        self.embedder = embedder or (
            lambda text: default_local_embedder(text, dim=vector_size)
        )
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )

    def add_policy(
        self, policy_id: str, content: str, metadata: dict[str, str] | None = None
    ) -> None:
        """Indexa una norma o documento técnico dentro de Qdrant."""
        point_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, policy_id))
        vector = self.embedder(content)
        payload = {"policy_id": policy_id, "content": content, **(metadata or {})}
        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=point_uuid, vector=vector, payload=payload)],
        )

    def verify_query(self, query: str) -> PolicyMatch:
        """Verifica si existe respaldo documental en Qdrant para evitar alucinaciones."""
        query_vector = self.embedder(query)
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=1,
        )

        if not response.points:
            return PolicyMatch(
                has_sufficient_backing=False, best_score=0.0, matched_policy=None
            )

        top_hit = response.points[0]
        score = float(top_hit.score)
        content = top_hit.payload.get("content") if top_hit.payload else None

        return PolicyMatch(
            has_sufficient_backing=score >= self.similarity_threshold,
            best_score=score,
            matched_policy=content,
        )
