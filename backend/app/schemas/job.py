from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    description_raw: str


class JobUpdate(BaseModel):
    title: str | None = None
    description_raw: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description_raw: str
    description_clean: str | None
    weight_semantic: float
    weight_skills: float
    weight_experience: float
    weight_education: float
    weight_certifications: float
    created_at: datetime


class JobWeightsUpdate(BaseModel):
    weight_semantic: float | None = None
    weight_skills: float | None = None
    weight_experience: float | None = None
    weight_education: float | None = None
    weight_certifications: float | None = None
