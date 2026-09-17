import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job
from app.db.session import get_db
from app.schemas.job import JobCreate, JobResponse, JobUpdate, JobWeightsUpdate


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)) -> Job:
    job = Job(
        title=job_data.title,
        description_raw=job_data.description_raw,
        required_skills=job_data.required_skills,
        experience_level=job_data.experience_level,
        job_type=job_data.job_type,
        work_mode=job_data.work_mode,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info("Created job %s", job.id)
    return job


@router.get("/", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.created_at.desc())).all())


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    for field, value in job_data.model_dump(exclude_none=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    logger.info("Updated job %s", job.id)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)) -> None:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    logger.info("Deleted job %s", job_id)


@router.put("/{job_id}/weights", response_model=JobResponse)
def update_job_weights(
    job_id: int,
    weights: JobWeightsUpdate,
    db: Session = Depends(get_db),
) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    for field, value in weights.model_dump(exclude_none=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    logger.info("Updated weights for job %s", job.id)
    return job
