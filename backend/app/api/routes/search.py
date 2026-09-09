import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Candidate, Job, Score
from app.db.session import get_db
from app.embeddings.cpu_backend import CPUEmbeddingBackend
from app.extraction.education_extractor import extract_certifications, extract_education
from app.extraction.skill_extractor import extract_experience_years, extract_skills
from app.ranking.scorer import (
    calculate_certification_score,
    calculate_education_score,
    calculate_experience_score,
    calculate_final_score,
    calculate_skills_score,
)
from app.vector_search.faiss_backend import FAISSBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["search"])

_embedding_backend = CPUEmbeddingBackend()


@router.post("/{job_id}/search")
def search_candidates(job_id: int, db: Session = Depends(get_db)) -> list[dict]:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = list(db.scalars(select(Candidate).where(Candidate.job_id == job_id)).all())
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates uploaded for this job")

    job_skills = extract_skills(job.description_raw)
    job_certifications = extract_certifications(job.description_raw)
    job_text = job.description_clean or job.description_raw
    job_vector = _embedding_backend.encode([job_text])[0]

    candidate_texts = [candidate.clean_text or candidate.raw_text or "" for candidate in candidates]
    candidate_vectors = _embedding_backend.encode(candidate_texts)

    search_index = FAISSBackend(dimension=len(job_vector))
    search_index.add(candidate_vectors, ids=[candidate.id for candidate in candidates])

    raw_results = search_index.search(job_vector, top_k=len(candidates))

    candidates_by_id = {candidate.id: candidate for candidate in candidates}
    ranked_results = []

    for candidate_id, semantic_score in raw_results:
        candidate = candidates_by_id[candidate_id]
        candidate_text = candidate.clean_text or candidate.raw_text or ""
        candidate_skills = extract_skills(candidate_text)
        candidate_years = extract_experience_years(candidate_text)
        candidate_education = extract_education(candidate_text)
        candidate_certifications = extract_certifications(candidate_text)

        skills_score = calculate_skills_score(candidate_skills, job_skills)
        experience_score = calculate_experience_score(candidate_years, None)
        education_score = calculate_education_score(candidate_education)
        certification_score = calculate_certification_score(candidate_certifications, job_certifications)

        final_score = calculate_final_score(
            semantic_score=semantic_score,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score,
            certification_score=certification_score,
            weight_semantic=job.weight_semantic,
            weight_skills=job.weight_skills,
            weight_experience=job.weight_experience,
            weight_education=job.weight_education,
            weight_certifications=job.weight_certifications,
        )

        score_row = Score(
            candidate_id=candidate.id,
            job_id=job.id,
            semantic_score=semantic_score,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score,
            certification_score=certification_score,
            final_score=final_score,
        )
        db.add(score_row)

        ranked_results.append(
            {
                "candidate_id": candidate.id,
                "filename": candidate.filename,
                "semantic_score": round(semantic_score, 4),
                "skills_score": round(skills_score, 4),
                "experience_score": round(experience_score, 4),
                "education_score": round(education_score, 4),
                "certification_score": round(certification_score, 4),
                "final_score": round(final_score, 4),
                "matched_skills": list(set(candidate_skills) & set(job_skills)),
                "education": candidate_education,
                "certifications": candidate_certifications,
            }
        )

    db.commit()
    ranked_results.sort(key=lambda item: item["final_score"], reverse=True)
    logger.info("Ranked %d candidates for job %s", len(ranked_results), job_id)
    return ranked_results
