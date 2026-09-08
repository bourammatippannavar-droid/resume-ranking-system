from abc import ABC, abstractmethod


class EmbeddingBackend(ABC):
    """Interface implemented by all CPU and GPU embedding backends."""

    @abstractmethod
    def encode(self, texts: list[str]) -> list[list[float]]:
        """Convert text strings into embedding vectors."""
        raise NotImplementedError
