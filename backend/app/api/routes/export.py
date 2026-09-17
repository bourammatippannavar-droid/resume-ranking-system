import csv
import io
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import Candidate, Job, Score
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["export"])


@router.get("/{job_id}/export")
def export_results_csv(job_id: int, db: Session = Depends(get_db)) -> StreamingResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    latest_score_subquery = (
        select(
            Score.candidate_id,
            func.max(Score.ranked_at).label("latest_ranked_at"),
        )
        .where(Score.job_id == job_id)
        .group_by(Score.candidate_id)
        .subquery()
    )

    rows = db.execute(
        select(Score, Candidate)
        .join(Candidate, Score.candidate_id == Candidate.id)
        .join(
            latest_score_subquery,
            (Score.candidate_id == latest_score_subquery.c.candidate_id)
            & (Score.ranked_at == latest_score_subquery.c.latest_ranked_at),
        )
        .where(Score.job_id == job_id)
        .order_by(Score.final_score.desc())
    ).all()

    if not rows:
        raise HTTPException(status_code=400, detail="No ranked results found. Run search first.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Filename", "Final Score", "Semantic Score", "Skills Score",
        "Experience Score", "Education Score", "Certification Score", "Notes",
    ])

    for rank, (score, candidate) in enumerate(rows, start=1):
        writer.writerow([
            rank,
            candidate.filename,
            round(score.final_score, 4) if score.final_score is not None else "",
            round(score.semantic_score, 4) if score.semantic_score is not None else "",
            round(score.skills_score, 4) if score.skills_score is not None else "",
            round(score.experience_score, 4) if score.experience_score is not None else "",
            round(score.education_score, 4) if score.education_score is not None else "",
            round(score.certification_score, 4) if score.certification_score is not None else "",
            candidate.notes or "",
        ])

    output.seek(0)
    logger.info("Exported CSV for job %s with %d rows", job_id, len(rows))

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}_results.csv"},
    )
