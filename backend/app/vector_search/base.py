from abc import ABC, abstractmethod


class VectorSearchBackend(ABC):
    """Interface implemented by all vector search backends (FAISS, Qdrant, cuVS)."""

    @abstractmethod
    def add(self, vectors: list[list[float]], ids: list[int]) -> None:
        """Add vectors to the index, tagged with their corresponding integer ids."""
        raise NotImplementedError

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int) -> list[tuple[int, float]]:
        """Search the index, returning up to top_k (id, similarity_score) pairs."""
        raise NotImplementedError
