from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    filename: str
    file_type: str
    status: str
    uploaded_at: datetime


class CandidateDetailResponse(CandidateResponse):
    clean_text: str | None
    notes: str | None


class CandidateNotesUpdate(BaseModel):
    notes: str


class CandidateStatusUpdate(BaseModel):
    status: str
