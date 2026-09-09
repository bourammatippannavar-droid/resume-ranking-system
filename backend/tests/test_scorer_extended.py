from app.ranking.scorer import calculate_certification_score, calculate_education_score


def test_calculate_education_score_with_entries():
    assert calculate_education_score([{"degree": "bachelor of engineering", "institutions": []}]) == 1.0


def test_calculate_education_score_no_entries():
    assert calculate_education_score([]) == 0.0


def test_calculate_certification_score_no_certifications():
    assert calculate_certification_score([], ["aws certified"]) == 0.0


def test_calculate_certification_score_no_job_requirement():
    assert calculate_certification_score(["aws certified"], None) == 1.0


def test_calculate_certification_score_full_match():
    assert calculate_certification_score(["pmp"], ["pmp"]) == 1.0


def test_calculate_certification_score_partial_match():
    assert calculate_certification_score(["pmp"], ["pmp", "itil"]) == 0.5
