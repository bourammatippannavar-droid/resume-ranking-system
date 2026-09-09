
Default weights: semantic 0.5, skills 0.2, experience 0.15, education 0.1, certifications 0.05. Weights are configurable per job via `PUT /api/v1/jobs/{id}/weights`.

Education and certification scoring are placeholders (return 0.0) pending future extraction work.

## Running Benchmarks

```powershell
cd backend
python -m app.benchmarking.runner --backend cpu --dataset-size 100 --repeats 3
```

For GPU benchmarking on a machine without a local NVIDIA GPU, the same script runs unmodified on Kaggle or Google Colab notebooks with a GPU accelerator:

```python
!git clone https://github.com/bourammatippannavar-droid/resume-ranking-system.git
%cd resume-ranking-system/backend
!pip install -q -r requirements.txt
!python -m app.benchmarking.runner --backend gpu --dataset-size 100 --repeats 3
```

Results append to `benchmark_result.json`.

## Testing

```powershell
cd backend
python -m pytest tests\ -v
```

15 tests covering ranking score calculations and skill/experience extraction.

## Known Limitations

- Education and certification extraction are not yet implemented; those score components currently return 0.0
- Skill extraction uses a fixed keyword list rather than NLP-based entity recognition
- Vector search rebuilds the FAISS index per search request rather than persisting it
- No frontend yet (planned)

## Roadmap

- [x] CPU and GPU embedding backends
- [x] FAISS vector search
- [x] Keyword-based skill extraction
- [x] Weighted ranking and search endpoint
- [x] Embedding benchmarks with real CPU/GPU comparison
- [ ] Minimal frontend for uploading resumes and viewing rankings
- [ ] Education/certification extraction
- [ ] Persistent vector index (avoid rebuilding per request)

## License

