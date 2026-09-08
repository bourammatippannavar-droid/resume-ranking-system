import logging
import time

import torch
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.embeddings.base import EmbeddingBackend


logger = logging.getLogger(__name__)


class GPUEmbeddingBackend(EmbeddingBackend):
    """Sentence-Transformers embedding backend running on an NVIDIA CUDA GPU."""

    def __init__(self) -> None:
        if not torch.cuda.is_available():
            raise RuntimeError(
                "GPUEmbeddingBackend requires a CUDA-capable GPU, but none was detected."
            )
        settings = get_settings()
        model_name = settings.EMBEDDING_MODEL_NAME
        logger.info("Loading embedding model '%s' on GPU (%s)", model_name, torch.cuda.get_device_name(0))
        self.model = SentenceTransformer(model_name, device="cuda")

    def encode(self, texts: list[str]) -> list[list[float]]:
        start_time = time.perf_counter()
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        elapsed = time.perf_counter() - start_time
        logger.info(
            "Encoded %d texts on GPU in %.4f seconds",
            len(texts),
            elapsed,
        )
        return embeddings.tolist()
