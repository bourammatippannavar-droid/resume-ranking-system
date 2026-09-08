import logging

logger = logging.getLogger(__name__)


def calculate_skills_score(candidate_skills: list[str], job_skills: list[str]) -> float:
    """Return the fraction of job-required skills present in the candidate's skills, 0.0 to 1.0."""
    if not job_skills:
        return 0.0
    matched = set(candidate_skills) & set(job_skills)
    return len(matched) / len(job_skills)


def calculate_experience_score(candidate_years: float | None, required_years: float | None) -> float:
    """Return 1.0 if candidate meets or exceeds required years, partial credit otherwise, 0.0 if unknown."""
    if candidate_years is None or required_years is None or required_years == 0:
        return 0.0
    return min(candidate_years / required_years, 1.0)


def calculate_final_score(
    semantic_score: float,
    skills_score: float,
    experience_score: float,
    education_score: float,
    certification_score: float,
    weight_semantic: float,
    weight_skills: float,
    weight_experience: float,
    weight_education: float,
    weight_certifications: float,
) -> float:
    """Combine individual component scores into a single weighted final score."""
    final_score = (
        semantic_score * weight_semantic
        + skills_score * weight_skills
        + experience_score * weight_experience
        + education_score * weight_education
        + certification_score * weight_certifications
    )
    logger.info("Calculated final score: %.4f", final_score)
    return final_score
