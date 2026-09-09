import logging
import os

from app.vector_search.faiss_backend import FAISSBackend

logger = logging.getLogger(__name__)

INDEX_DIR = "indexes"
EMBEDDING_DIMENSION = 384


def _index_path(job_id: int) -> str:
    os.makedirs(INDEX_DIR, exist_ok=True)
    return os.path.join(INDEX_DIR, f"job_{job_id}.faiss")


def load_or_create_index(job_id: int) -> FAISSBackend:
    """Load a job's persisted FAISS index if it exists, otherwise create a new empty one."""
    path = _index_path(job_id)
    if os.path.exists(path):
        return FAISSBackend.load(path, dimension=EMBEDDING_DIMENSION)
    logger.info("No existing index for job %s, creating new one", job_id)
    return FAISSBackend(dimension=EMBEDDING_DIMENSION)


def save_index(job_id: int, backend: FAISSBackend) -> None:
    """Persist a job's FAISS index to disk."""
    backend.save(_index_path(job_id))
