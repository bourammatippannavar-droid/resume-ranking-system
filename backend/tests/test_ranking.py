from app.ranking.scorer import (
    calculate_experience_score,
    calculate_final_score,
    calculate_skills_score,
)


def test_calculate_skills_score_full_match():
    assert calculate_skills_score(["python", "fastapi"], ["python", "fastapi"]) == 1.0


def test_calculate_skills_score_partial_match():
    assert calculate_skills_score(["python"], ["python", "fastapi"]) == 0.5


def test_calculate_skills_score_no_match():
    assert calculate_skills_score(["java"], ["python", "fastapi"]) == 0.0


def test_calculate_skills_score_empty_job_skills():
    assert calculate_skills_score(["python"], []) == 0.0


def test_calculate_experience_score_meets_requirement():
    assert calculate_experience_score(5.0, 3.0) == 1.0


def test_calculate_experience_score_below_requirement():
    assert calculate_experience_score(1.5, 3.0) == 0.5


def test_calculate_experience_score_unknown_candidate_years():
    assert calculate_experience_score(None, 3.0) == 0.0


def test_calculate_experience_score_unknown_required_years():
    assert calculate_experience_score(5.0, None) == 0.0


def test_calculate_final_score_weighted_sum():
    score = calculate_final_score(
        semantic_score=0.8,
        skills_score=1.0,
        experience_score=0.5,
        education_score=0.0,
        certification_score=0.0,
        weight_semantic=0.5,
        weight_skills=0.2,
        weight_experience=0.15,
        weight_education=0.1,
        weight_certifications=0.05,
    )
    expected = 0.8 * 0.5 + 1.0 * 0.2 + 0.5 * 0.15
    assert abs(score - expected) < 1e-9
