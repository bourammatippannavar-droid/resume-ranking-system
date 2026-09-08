import logging
import time

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.embeddings.base import EmbeddingBackend


logger = logging.getLogger(__name__)


class CPUEmbeddingBackend(EmbeddingBackend):
    """Sentence-Transformers embedding backend forced to run on CPU."""

    def __init__(self) -> None:
        settings = get_settings()
        model_name = settings.EMBEDDING_MODEL_NAME
        logger.info("Loading embedding model '%s' on CPU", model_name)
        self.model = SentenceTransformer(model_name, device="cpu")

    def encode(self, texts: list[str]) -> list[list[float]]:
        start_time = time.perf_counter()
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        elapsed = time.perf_counter() - start_time
        logger.info(
            "Encoded %d texts on CPU in %.4f seconds",
            len(texts),
            elapsed,
        )
        return embeddings.tolist()
