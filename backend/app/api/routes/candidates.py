import logging
import os
import tempfile
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Candidate, Job
from app.db.session import get_db
from app.parsing.docx_parser import DOCXParsingError, extract_text_from_docx
from app.parsing.pdf_parser import PDFParsingError, extract_text_from_pdf
from app.parsing.text_cleaner import clean_text
from app.schemas.candidate import CandidateDetailResponse, CandidateResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["candidates"])


@router.post("/{job_id}/candidates")
def upload_candidates(
    job_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if db.get(Job, job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")

    created: list[Candidate] = []
    failed: list[dict[str, str]] = []

    for uploaded_file in files:
        filename = uploaded_file.filename or "unnamed"
        extension = os.path.splitext(filename)[1].lower()
        if extension not in {".pdf", ".docx"}:
            failed.append({"filename": filename, "reason": "Unsupported file type"})
            continue

        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temporary_file:
                temporary_path = temporary_file.name
                while chunk := uploaded_file.file.read(1024 * 1024):
                    temporary_file.write(chunk)

            if extension == ".pdf":
                raw_text = extract_text_from_pdf(temporary_path)
                file_type = "pdf"
            else:
                raw_text = extract_text_from_docx(temporary_path)
                file_type = "docx"

            candidate = Candidate(
                job_id=job_id,
                filename=filename,
                raw_text=raw_text,
                clean_text=clean_text(raw_text),
                file_type=file_type,
            )
            db.add(candidate)
            created.append(candidate)
        except (PDFParsingError, DOCXParsingError) as exc:
            logger.error("Failed to parse uploaded file %s: %s", filename, exc)
            failed.append({"filename": filename, "reason": str(exc)})
        except Exception as exc:
            logger.error("Failed to process uploaded file %s: %s", filename, exc)
            failed.append({"filename": filename, "reason": str(exc)})
        finally:
            if temporary_path:
                os.unlink(temporary_path)

    db.commit()
    for candidate in created:
        db.refresh(candidate)

    logger.info(
        "Processed candidate uploads for job %s: %d created, %d failed",
        job_id,
        len(created),
        len(failed),
    )
    return {
        "created": [CandidateResponse.model_validate(candidate) for candidate in created],
        "failed": failed,
    }


@router.get("/{job_id}/candidates", response_model=list[CandidateResponse])
def list_candidates(job_id: int, db: Session = Depends(get_db)) -> list[Candidate]:
    if db.get(Job, job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return list(
        db.scalars(select(Candidate).where(Candidate.job_id == job_id)).all()
    )


@router.get(
    "/{job_id}/candidates/{candidate_id}",
    response_model=CandidateDetailResponse,
)
def get_candidate(
    job_id: int,
    candidate_id: int,
    db: Session = Depends(get_db),
) -> Candidate:
    candidate = db.scalar(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.job_id == job_id,
        )
    )
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
