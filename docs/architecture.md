# Architecture

## Overview

This system ranks candidate resumes against a job description using a pipeline of text extraction, semantic embedding, vector search, and weighted multi-factor scoring. The core research contribution is a modular CPU/GPU embedding backend, benchmarked to quantify real GPU acceleration gains for this workload.

## Pipeline

## Design Decisions

### Modular embedding backend (CPU/GPU)

app/embeddings/base.py defines an abstract EmbeddingBackend interface with one method, encode(). CPUEmbeddingBackend and GPUEmbeddingBackend both implement it identically from the callers perspective; app/embeddings/factory.py selects between them based on the EMBEDDING_DEVICE environment variable, with automatic fallback to CPU if a GPU is requested but unavailable.

This means the rest of the application never imports a concrete backend directly. Swapping hardware is a one-line environment variable change, not a code change. This was validated in practice: the exact same benchmarking/runner.py script ran unmodified on a local CPU-only laptop and on a Kaggle GPU notebook.


### Persistent, incremental vector index

Early versions rebuilt the FAISS index from scratch on every search request, re-embedding every candidate each time. This works but wastes computation as the candidate pool grows. The current design (app/vector_search/index_manager.py) builds the index once per job, incrementally adds vectors when new candidates are uploaded, and persists it to disk (backend/indexes/job_{id}.faiss). Search requests load the existing index rather than rebuilding it, which is both faster and allows indexing time to be benchmarked separately from query time - a requirement of the original project brief.

### Five-component weighted scoring

Final ranking combines five independently-computed scores (semantic similarity, skills match, experience match, education presence, certification match), each weighted per job and configurable via PUT /api/v1/jobs/{id}/weights. Weights are stored on the Job row rather than hardcoded, so different roles can prioritize different signals without a code change.

### Education/certification extraction: NER + regex, not a single technique

Resume education sections are irregularly formatted and do not fit cleanly into any single extraction approach. The final design combines regex patterns for degree types, spaCy general-purpose NER for institution names, and proximity filtering plus keyword validation to suppress false positives.

This was arrived at iteratively: an initial raw-NER approach produced noisy results (section headers and product names misclassified as organizations); proximity filtering and keyword validation each measurably improved precision, tested against a real resume at each step. This is documented as a known limitation rather than treated as solved.


### Model warm-up at startup

Both the embedding model and the spaCy pipeline have meaningful first-call latency (CUDA context initialization for GPU embeddings; internal spaCy setup for NLP). Rather than let the first real user request absorb this cost, app/main.py runs a lifespan startup hook that triggers both models once before the server begins accepting traffic. This was discovered as a real issue during testing (first search request timed out at 30 seconds; subsequent requests completed in under a second) and fixed rather than worked around.

## Benchmarking Methodology

The benchmarking module (app/benchmarking/runner.py) runs as a standalone script, independent of the API server, so it can execute in any Python environment - including a Kaggle notebook with GPU access, with no code changes.

Key methodological choices:

- Warmup exclusion: the first call to any backend includes one-time initialization cost. Each benchmark run performs one untimed warmup call before the timed repeats, so reported numbers reflect steady-state performance, not first-call overhead. This was identified after an initial GPU benchmark showed GPU throughput lower than CPU, purely an artifact of the first calls CUDA initialization dominating a small 3-run average, and corrected once diagnosed.
- Multiple repeats, reported as mean: every benchmark runs 3 or more times; the mean is reported alongside the full list of individual durations for transparency.
- Real hardware, no fabricated numbers: all reported figures come from actual runs (local CPU laptop; NVIDIA Tesla T4 via Kaggle free tier). Raw results are committed to backend/benchmark_result.json.

## Known Limitations and Future Work

- FAISS runs on CPU in this version; a GPU-accelerated index (faiss-gpu or NVIDIA cuVS) was identified as the natural next step for vector search itself, distinct from embedding generation
- Qdrant was evaluated as a second vector search backend to demonstrate the abstraction is real, but deprioritized due to local Docker/WSL2 setup constraints
- Docker configuration is written and reviewed but not locally verified end-to-end, for the same environment reason
- Education/certification extraction uses general-purpose NER rather than a resume-specific model or dataset
