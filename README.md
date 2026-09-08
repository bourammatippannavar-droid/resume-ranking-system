# Resume Ranking System

A backend service for ranking candidate resumes against job descriptions using semantic search, keyword-based skill extraction, and configurable weighted scoring.

## Features

- **Resume parsing** - extracts text from PDF and DOCX resumes
- **Semantic ranking** - planned FAISS and Sentence-Transformers integration
- **Skill extraction** - planned keyword-based extraction from resume text
- **Weighted scoring** - configurable per-job scoring weights
- **CPU/GPU embedding backends** - planned backend selection with CPU fallback
- **REST API** - FastAPI with PostgreSQL and SQLAlchemy support
- **Benchmarking** - planned standalone embedding benchmark runner

## Tech Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Embeddings | Sentence-Transformers, CPU/GPU backends |
| Vector search | FAISS |
| Parsing | PyMuPDF, python-docx |
| Validation | Pydantic v2 |
| Testing | pytest |

## Project Structure

```text
backend/
├── app/
│   ├── api/routes/          # FastAPI route handlers
│   ├── core/                # Application configuration
│   ├── db/                  # SQLAlchemy models and session management
│   ├── embeddings/          # Embedding backend interfaces
│   ├── extraction/          # Extraction utilities
│   ├── parsing/             # PDF/DOCX parsing and text cleaning
│   ├── ranking/             # Ranking logic
│   ├── schemas/             # Pydantic request/response schemas
│   ├── vector_search/       # Vector search integration
│   └── main.py              # FastAPI application entry point
├── requirements.txt
└── requirements-gpu.txt
frontend/                    # Planned frontend
docs/                        # Architecture documentation
```

## Setup

### Prerequisites

- Python 3.13 recommended
- PostgreSQL 17

### Installation

```powershell
git clone https://github.com/bourammatippannavar-droid/resume-ranking-system.git
cd resume-ranking-system

py -3.13 -m venv backend\venv
backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### Environment Configuration

Copy the example environment file and update the values for your machine:

```powershell
Copy-Item .env.example backend\.env
```

Example configuration:

```dotenv
DATABASE_URL=postgresql://username:password@localhost:5432/resume_ranking
EMBEDDING_DEVICE=cpu
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
VECTOR_BACKEND=faiss
LOG_LEVEL=INFO
```

Use `EMBEDDING_DEVICE=cuda` when a compatible GPU environment is configured.

### Database Setup

Create the PostgreSQL database:

```sql
CREATE DATABASE resume_ranking;
```

The SQLAlchemy models and `create_all_tables()` helper are available in `backend/app/db`.

## Running the API

```powershell
cd backend
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive documentation is available at `http://localhost:8000/docs`.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Database connectivity check |
| POST | `/api/v1/jobs/` | Create a job |
| GET | `/api/v1/jobs/{id}` | Fetch a job |
| PUT | `/api/v1/jobs/{id}/weights` | Update job scoring weights |
| POST | `/api/v1/jobs/{id}/candidates` | Upload and parse PDF/DOCX resumes |
| GET | `/api/v1/jobs/{id}/candidates` | List candidates for a job |
| GET | `/api/v1/jobs/{id}/candidates/{candidate_id}` | Fetch candidate details |

Ranking search endpoints are planned as part of the ranking and vector-search implementation.

## Scoring

The scoring pipeline is planned to combine:

1. Semantic similarity between job and resume embeddings
2. Skill overlap from extracted candidate skills
3. Experience and education signals
4. Per-job configurable weights

## Testing

```powershell
cd backend
pytest
```

Test coverage is currently a work in progress.

## Roadmap

- [ ] Implement CPU and GPU embedding backends
- [ ] Add FAISS vector search
- [ ] Add keyword-based skill extraction
- [ ] Implement weighted ranking and search endpoints
- [ ] Add embedding benchmarks, including GPU comparisons
- [ ] Add a minimal frontend for uploading resumes and viewing rankings
- [ ] Expand pytest coverage

## License

TBD
