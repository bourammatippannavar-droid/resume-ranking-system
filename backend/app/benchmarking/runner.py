import argparse
import json
import logging
import time
from pathlib import Path

from app.embeddings.cpu_backend import CPUEmbeddingBackend
from app.vector_search.faiss_backend import FAISSBackend

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


SAMPLE_TEXTS = [
    "Experienced software developer skilled in Python, FastAPI, and PostgreSQL, "
    "with a strong background in building scalable REST APIs and microservices.",
    "Data scientist with expertise in machine learning, deep learning, and NLP, "
    "using PyTorch and TensorFlow for production-grade model deployment.",
    "Frontend engineer specializing in React, TypeScript, and modern responsive "
    "web design, with experience in agile development environments.",
    "DevOps engineer proficient in Docker, Kubernetes, AWS, and CI/CD pipelines, "
    "focused on infrastructure automation and reliability engineering.",
    "Backend developer with strong Java and Spring Boot experience, building "
    "high-throughput distributed systems and RESTful services.",
]


def get_gpu_memory_stats() -> dict | None:
    """Return GPU memory usage stats if CUDA is available, else None."""
    try:
        import torch
        if not torch.cuda.is_available():
            return None
        return {
            "allocated_mb": round(torch.cuda.memory_allocated() / (1024 ** 2), 2),
            "reserved_mb": round(torch.cuda.memory_reserved() / (1024 ** 2), 2),
            "max_allocated_mb": round(torch.cuda.max_memory_allocated() / (1024 ** 2), 2),
        }
    except ImportError:
        return None


def run_embedding_benchmark(backend_name: str, dataset_size: int, repeats: int = 3) -> dict:
    """Run repeated embedding generation and report timing statistics."""
    texts = (SAMPLE_TEXTS * ((dataset_size // len(SAMPLE_TEXTS)) + 1))[:dataset_size]

    if backend_name == "gpu":
        from app.embeddings.gpu_backend import GPUEmbeddingBackend
        backend = GPUEmbeddingBackend()
        import torch
        torch.cuda.reset_peak_memory_stats()
    else:
        backend = CPUEmbeddingBackend()

    backend.encode(texts)

    durations = []
    for run_index in range(repeats):
        start_time = time.perf_counter()
        backend.encode(texts)
        elapsed = time.perf_counter() - start_time
        durations.append(elapsed)
        logger.info("Run %d/%d: %.4f seconds for %d texts", run_index + 1, repeats, elapsed, dataset_size)

    mean_time = sum(durations) / len(durations)
    throughput = dataset_size / mean_time

    result = {
        "operation": "embedding_generation",
        "backend": backend_name,
        "dataset_size": dataset_size,
        "repeats": repeats,
        "durations_seconds": durations,
        "mean_time_seconds": round(mean_time, 4),
        "throughput_texts_per_second": round(throughput, 2),
        "gpu_memory": get_gpu_memory_stats() if backend_name == "gpu" else None,
    }
    return result


def run_indexing_benchmark(backend_name: str, dataset_size: int, repeats: int = 3) -> dict:
    """Measure how long it takes to build a FAISS index for a given number of vectors."""
    texts = (SAMPLE_TEXTS * ((dataset_size // len(SAMPLE_TEXTS)) + 1))[:dataset_size]

    if backend_name == "gpu":
        from app.embeddings.gpu_backend import GPUEmbeddingBackend
        embedding_backend = GPUEmbeddingBackend()
    else:
        embedding_backend = CPUEmbeddingBackend()

    vectors = embedding_backend.encode(texts)
    ids = list(range(dataset_size))

    durations = []
    for run_index in range(repeats):
        index = FAISSBackend(dimension=len(vectors[0]))
        start_time = time.perf_counter()
        index.add(vectors, ids)
        elapsed = time.perf_counter() - start_time
        durations.append(elapsed)
        logger.info("Indexing run %d/%d: %.4f seconds for %d vectors", run_index + 1, repeats, elapsed, dataset_size)

    mean_time = sum(durations) / len(durations)

    result = {
        "operation": "indexing",
        "backend": backend_name,
        "dataset_size": dataset_size,
        "repeats": repeats,
        "durations_seconds": durations,
        "mean_time_seconds": round(mean_time, 4),
        "vectors_per_second": round(dataset_size / mean_time, 2),
    }
    return result


def run_query_latency_benchmark(backend_name: str, dataset_size: int, repeats: int = 5) -> dict:
    """Measure pure FAISS query latency, excluding embedding generation time."""
    texts = (SAMPLE_TEXTS * ((dataset_size // len(SAMPLE_TEXTS)) + 1))[:dataset_size]

    if backend_name == "gpu":
        from app.embeddings.gpu_backend import GPUEmbeddingBackend
        embedding_backend = GPUEmbeddingBackend()
    else:
        embedding_backend = CPUEmbeddingBackend()

    vectors = embedding_backend.encode(texts)
    ids = list(range(dataset_size))
    index = FAISSBackend(dimension=len(vectors[0]))
    index.add(vectors, ids)

    query_vector = vectors[0]
    index.search(query_vector, top_k=10)

    durations = []
    for run_index in range(repeats):
        start_time = time.perf_counter()
        index.search(query_vector, top_k=10)
        elapsed = time.perf_counter() - start_time
        durations.append(elapsed)

    mean_time = sum(durations) / len(durations)

    result = {
        "operation": "query_latency",
        "backend": backend_name,
        "dataset_size": dataset_size,
        "repeats": repeats,
        "durations_seconds": durations,
        "mean_time_seconds": round(mean_time, 6),
        "mean_time_ms": round(mean_time * 1000, 3),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CPU/GPU embedding and vector search benchmarks")
    parser.add_argument("--backend", choices=["cpu", "gpu"], required=True)
    parser.add_argument("--dataset-size", type=int, default=50)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=str, default="benchmark_result.json")
    parser.add_argument(
        "--operation",
        choices=["embedding", "indexing", "query_latency", "all"],
        default="embedding",
    )
    args = parser.parse_args()

    results = []
    if args.operation in ("embedding", "all"):
        results.append(run_embedding_benchmark(args.backend, args.dataset_size, args.repeats))
    if args.operation in ("indexing", "all"):
        results.append(run_indexing_benchmark(args.backend, args.dataset_size, args.repeats))
    if args.operation in ("query_latency", "all"):
        results.append(run_query_latency_benchmark(args.backend, args.dataset_size, args.repeats))

    output_path = Path(args.output)
    existing_results = []
    if output_path.exists():
        existing_results = json.loads(output_path.read_text())

    existing_results.extend(results)
    output_path.write_text(json.dumps(existing_results, indent=2))

    logger.info("Benchmark complete. %d result(s) appended to %s", len(results), output_path)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
