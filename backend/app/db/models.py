from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description_raw: Mapped[str] = mapped_column(Text, nullable=False)
    description_clean: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_semantic: Mapped[float] = mapped_column(Float, default=0.5)
    weight_skills: Mapped[float] = mapped_column(Float, default=0.2)
    weight_experience: Mapped[float] = mapped_column(Float, default=0.15)
    weight_education: Mapped[float] = mapped_column(Float, default=0.1)
    weight_certifications: Mapped[float] = mapped_column(Float, default=0.05)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    candidates: Mapped[list["Candidate"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    clean_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    job: Mapped[Job] = relationship(back_populates="candidates")
    candidate_profile: Mapped["CandidateProfile | None"] = relationship(
        back_populates="candidate",
        uselist=False,
        cascade="all, delete-orphan",
    )


class CandidateProfile(Base):
    __tablename__ = "candidate_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        unique=True,
        nullable=False,
    )
    skills: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    education: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    certifications: Mapped[Any | None] = mapped_column(JSON, nullable=True)

    candidate: Mapped[Candidate] = relationship(back_populates="candidate_profile")


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=True,
    )
    job_id: Mapped[int | None] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=True,
    )
    vector_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dim: Mapped[int] = mapped_column(Integer, nullable=False)
    backend_used: Mapped[str] = mapped_column(String(20), nullable=False)


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    semantic_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    skills_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    education_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    certification_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ranked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

