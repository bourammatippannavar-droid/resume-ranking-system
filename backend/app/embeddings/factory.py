import logging

from app.core.config import get_settings
from app.embeddings.base import EmbeddingBackend
from app.embeddings.cpu_backend import CPUEmbeddingBackend

logger = logging.getLogger(__name__)


def get_embedding_backend() -> EmbeddingBackend:
    """Return the configured embedding backend, based on EMBEDDING_DEVICE setting."""
    settings = get_settings()
    device = settings.EMBEDDING_DEVICE.lower()

    if device == "cuda" or device == "gpu":
        try:
            from app.embeddings.gpu_backend import GPUEmbeddingBackend
            logger.info("Using GPU embedding backend")
            return GPUEmbeddingBackend()
        except RuntimeError as exc:
            logger.warning("GPU backend requested but unavailable (%s); falling back to CPU", exc)
            return CPUEmbeddingBackend()

    logger.info("Using CPU embedding backend")
    return CPUEmbeddingBackend()
