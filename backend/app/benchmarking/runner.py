import argparse
import json
import logging
import time
from pathlib import Path

from app.embeddings.cpu_backend import CPUEmbeddingBackend

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


def run_embedding_benchmark(backend_name: str, dataset_size: int, repeats: int = 3) -> dict:
    """Run repeated embedding generation and report timing statistics."""
    texts = (SAMPLE_TEXTS * ((dataset_size // len(SAMPLE_TEXTS)) + 1))[:dataset_size]

    if backend_name == "gpu":
        from app.embeddings.gpu_backend import GPUEmbeddingBackend
        backend = GPUEmbeddingBackend()
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
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CPU/GPU embedding benchmarks")
    parser.add_argument("--backend", choices=["cpu", "gpu"], required=True)
    parser.add_argument("--dataset-size", type=int, default=50)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=str, default="benchmark_result.json")
    args = parser.parse_args()

    result = run_embedding_benchmark(args.backend, args.dataset_size, args.repeats)

    output_path = Path(args.output)
    existing_results = []
    if output_path.exists():
        existing_results = json.loads(output_path.read_text())

    existing_results.append(result)
    output_path.write_text(json.dumps(existing_results, indent=2))

    logger.info("Benchmark complete. Result appended to %s", output_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
