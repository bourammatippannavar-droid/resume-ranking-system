import logging
import time

import faiss
import numpy as np

from app.vector_search.base import VectorSearchBackend


logger = logging.getLogger(__name__)


class FAISSBackend(VectorSearchBackend):
    """FAISS-based vector search backend using cosine similarity via inner product."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.index = faiss.IndexIDMap(faiss.IndexFlatIP(dimension))
        logger.info("Initialized FAISS index with dimension %d", dimension)

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        return vectors / norms

    def add(self, vectors: list[list[float]], ids: list[int]) -> None:
        start_time = time.perf_counter()
        vector_array = np.array(vectors, dtype=np.float32)
        vector_array = self._normalize(vector_array)
        id_array = np.array(ids, dtype=np.int64)
        self.index.add_with_ids(vector_array, id_array)
        elapsed = time.perf_counter() - start_time
        logger.info(
            "Added %d vectors to FAISS index in %.4f seconds",
            len(vectors),
            elapsed,
        )

    def search(self, query_vector: list[float], top_k: int) -> list[tuple[int, float]]:
        start_time = time.perf_counter()
        query_array = np.array([query_vector], dtype=np.float32)
        query_array = self._normalize(query_array)
        scores, indices = self.index.search(query_array, top_k)
        elapsed = time.perf_counter() - start_time
        logger.info(
            "FAISS search completed in %.4f seconds, returned %d results",
            elapsed,
            len(indices[0]),
        )
        results = [
            (int(idx), float(score))
            for idx, score in zip(indices[0], scores[0])
            if idx != -1
        ]
        return results

    def contains_id(self, candidate_id: int) -> bool:
        """Check whether a given id is already present in the index."""
        return self.index.id_map.at(0) is not None and candidate_id in [
            self.index.id_map.at(i) for i in range(self.index.ntotal)
        ]

    def save(self, path: str) -> None:
        """Persist the FAISS index to disk."""
        faiss.write_index(self.index, path)
        logger.info("Saved FAISS index to %s (%d vectors)", path, self.index.ntotal)

    @classmethod
    def load(cls, path: str, dimension: int) -> "FAISSBackend":
        """Load a previously persisted FAISS index from disk."""
        backend = cls(dimension=dimension)
        backend.index = faiss.read_index(path)
        logger.info("Loaded FAISS index from %s (%d vectors)", path, backend.index.ntotal)
        return backend
