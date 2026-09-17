# Resume Ranking System

A GPU-accelerated backend service for ranking candidate resumes against job descriptions using semantic search, skill/education/certification extraction, and configurable weighted scoring. Includes comprehensive, real, measured CPU vs GPU performance benchmarking.

## Features

- **Resume parsing** - extracts text from PDF and DOCX resumes (PyMuPDF, python-docx)
- **Semantic ranking** - Sentence-Transformers embeddings + persistent FAISS vector search
- **Skill extraction** - keyword-based extraction of technical skills and experience years
- **Education & certification extraction** - spaCy NER + regex degree patterns with proximity-based institution matching, keyword-based certification detection
- **Weighted scoring** - fully configurable per-job scoring weights across all 5 components (semantic, skills, experience, education, certifications)
- **CPU/GPU embedding backends** - modular backend selection via factory pattern, automatic CPU fallback
- **Persistent vector index** - FAISS index built incrementally on upload, persisted to disk, not rebuilt per search
- **REST API** - FastAPI with PostgreSQL and SQLAlchemy
- **Benchmarking** - standalone benchmark runner covering embedding throughput, indexing speed, query latency, and GPU memory usage

## Benchmark Results

Measured on a local CPU (laptop) vs NVIDIA Tesla T4 GPU (Kaggle, free tier), using Sentence-Transformers all-MiniLM-L6-v2. All numbers are real measurements, 3 repeats each, one warmup run excluded from timing to avoid CUDA initialization bias. Raw data in backend/benchmark_result.json.

### Embedding generation throughput

| Dataset Size | CPU (texts/sec) | GPU (texts/sec) | Speedup |
| --- | --- | --- | --- |
| 20 | 122.81 | 1,293.02 | 10.5x |
| 100 | 149.67 | 1,658.33 | 11.1x |
| 500 | 161.10 | 2,985.48 | 18.5x |

GPU speedup generally increases with dataset size, consistent with better GPU parallelization at larger batch sizes.

### Vector search: indexing and query latency (dataset size 100)

| Metric | CPU | GPU-sourced vectors | Speedup |
| --- | --- | --- | --- |
| Indexing | 33,365.96 vectors/sec | 45,191.58 vectors/sec | 1.35x |
| Query latency | 2.939 ms | 0.214 ms | 13.7x |

FAISS itself runs on CPU in both rows (this project uses faiss-cpu); the GPU column reflects vectors produced by the GPU embedding backend, then indexed/queried with the same CPU-based FAISS index. Both indexing and querying are extremely fast at this scale (sub-3ms), meaning embedding generation - not vector search - is the dominant cost in this pipeline. This is why GPU acceleration specifically targets the embedding step. A true GPU-accelerated index (via faiss-gpu or NVIDIA cuVS) was identified as a natural next step but not implemented in this version.

### GPU memory footprint

At dataset size 100, the GPU backend used approximately 96 MB allocated (146 MB reserved) for the all-MiniLM-L6-v2 model and its working memory - a modest footprint given the small model size.

## Tech Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Embeddings | Sentence-Transformers, CPU/GPU backends via PyTorch |
| Vector search | FAISS (cosine similarity via normalized inner product), persisted per job |
| NLP extraction | spaCy (education/institution NER), regex (degrees, skills, certifications) |
| Parsing | PyMuPDF, python-docx |
| Validation | Pydantic v2 |
| Testing | pytest (21 passing tests) |

## Project Structure

backend/
- app/
  - api/routes/          # FastAPI route handlers (jobs, candidates, search)
  - core/                # Application configuration
  - db/                  # SQLAlchemy models and session management
  - embeddings/          # CPU/GPU embedding backends + factory
  - extraction/          # Skill, experience, education, certification extraction
  - parsing/             # PDF/DOCX parsing and text cleaning
  - ranking/             # Weighted scoring logic (5 components)
  - schemas/             # Pydantic request/response schemas
  - vector_search/       # FAISS backend + persistent index manager
  - benchmarking/        # Standalone CPU/GPU/indexing/query benchmark runner
  - main.py              # FastAPI application entry point, model warm-up
- indexes/               # Persisted FAISS indexes (gitignored, generated per job)
- tests/                 # pytest unit tests
- benchmark_result.json  # Real measured CPU/GPU benchmark data
- requirements.txt
- requirements-gpu.txt

frontend/                # Planned frontend
docs/                    # Architecture documentation

## Setup

### Prerequisites

- Python 3.13 recommended (avoid 3.14 - some ML packages lack prebuilt wheels)
- PostgreSQL 17

### Installation

git clone https://github.com/bourammatippannavar-droid/resume-ranking-system.git
cd resume-ranking-system

py -3.13 -m venv backend\venv
backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m spacy download en_core_web_sm

### Environment Configuration

Copy-Item .env.example backend\.env

Then edit backend\.env with your actual database credentials:

DATABASE_URL=postgresql://username:password@localhost:5432/resume_ranking
EMBEDDING_DEVICE=cpu
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
VECTOR_BACKEND=faiss
LOG_LEVEL=INFO

Set EMBEDDING_DEVICE=cuda when running on a machine with a compatible NVIDIA GPU.

### Database Setup

CREATE DATABASE resume_ranking;

Then create the tables:

cd backend
python -c "from app.db.session import create_all_tables; create_all_tables()"

## Running the API

cd backend
uvicorn app.main:app --reload

API available at http://localhost:8000. Interactive docs at http://localhost:8000/docs. Note: the first request after startup includes a brief NLP model warm-up (handled automatically at server startup, not on the first user request).

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /health | Database connectivity check |
| POST | /api/v1/jobs/ | Create a job with default scoring weights |
| GET | /api/v1/jobs/{id} | Fetch a job |
| PUT | /api/v1/jobs/{id}/weights | Update job scoring weights |
| POST | /api/v1/jobs/{id}/candidates | Upload resumes (PDF/DOCX) - parses, cleans, stores text, and incrementally indexes into the job's FAISS index |
| GET | /api/v1/jobs/{id}/candidates | List candidates for a job |
| GET | /api/v1/jobs/{id}/candidates/{candidate_id} | Fetch full candidate detail including cleaned text |
| POST | /api/v1/jobs/{id}/search | Run semantic search + ranking: loads the job's persisted FAISS index, extracts skills/education/certifications, computes weighted final scores, returns ranked results |

## Scoring

Final score is a configurable weighted combination of all 5 components:

final_score = semantic_score * weight_semantic + skills_score * weight_skills + experience_score * weight_experience + education_score * weight_education + certification_score * weight_certifications

Default weights: semantic 0.5, skills 0.2, experience 0.15, education 0.1, certifications 0.05. Weights are configurable per job via PUT /api/v1/jobs/{id}/weights.

- Semantic score: cosine similarity between job description and resume embeddings
- Skills score: fraction of job-required skills found in the resume
- Experience score: candidate years vs required years (partial credit if under)
- Education score: presence of a detected degree (1.0 if any found, else 0.0)
- Certification score: match fraction against job-required certifications, or presence-based if none specified

## Running Benchmarks

cd backend
python -m app.benchmarking.runner --backend cpu --dataset-size 100 --repeats 3 --operation all

The --operation flag accepts embedding, indexing, query_latency, or all.

For GPU benchmarking on a machine without a local NVIDIA GPU, the same script runs unmodified on Kaggle or Google Colab notebooks with a GPU accelerator:

!git clone https://github.com/bourammatippannavar-droid/resume-ranking-system.git
%cd resume-ranking-system/backend
!pip install -q -r requirements.txt
!python -m app.benchmarking.runner --backend gpu --dataset-size 100 --repeats 3 --operation all

Results append to benchmark_result.json.

## Testing

cd backend
python -m pytest tests\ -v

21 tests covering ranking score calculations (all 5 components) and skill/education/certification extraction.

## Known Limitations

- Vector search (FAISS) runs on CPU in both CPU and GPU benchmark modes; a fully GPU-accelerated index (faiss-gpu or NVIDIA cuVS) was evaluated but not implemented due to environment constraints
- Qdrant was considered as a second vector search backend to demonstrate architecture modularity, but deprioritized due to infrastructure setup time; the abstract VectorSearchBackend interface supports adding it without changing calling code
- Education extraction uses general-purpose NER (spaCy en_core_web_sm), which is not resume-specific and occasionally produces incomplete institution names
- Skill and certification extraction use fixed keyword lists rather than open-vocabulary NLP recognition
- No frontend yet (planned)

## Roadmap

- [x] CPU and GPU embedding backends
- [x] FAISS vector search with persistent, incrementally-updated indexes
- [x] Keyword-based skill extraction
- [x] spaCy-based education and certification extraction
- [x] Full 5-component weighted ranking and search endpoint
- [x] Comprehensive benchmarks: embedding throughput, indexing speed, query latency, GPU memory
- [x] Model warm-up at startup to avoid cold-start latency
- [ ] Minimal frontend for uploading resumes and viewing rankings
- [ ] Qdrant backend as a second vector search implementation
- [ ] GPU-accelerated vector search (faiss-gpu or cuVS)

## License

TBD

## Docker

Dockerfiles are provided for both backend and frontend, plus a docker-compose.yml orchestrating both services alongside PostgreSQL.

```powershell
docker-compose up --build
```

This starts Postgres, runs database migrations implicitly via the backend's startup, and serves the frontend via nginx on port 5173, proxying API calls to the backend on port 8000.

**Note**: Docker configuration is provided and reviewed for correctness, but could not be locally verified end-to-end due to WSL2/Docker Desktop initialization issues encountered on the development machine (Windows virtualization feature conflicts). The Dockerfiles follow standard, well-established patterns (multi-stage build for the frontend, slim Python base with spaCy model download for the backend) and are expected to work in a properly configured Docker environment.
