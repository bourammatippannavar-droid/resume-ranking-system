from app.extraction.skill_extractor import extract_experience_years, extract_skills


def test_extract_skills_finds_known_skills():
    text = "Experienced in Python, FastAPI, and PostgreSQL development."
    skills = extract_skills(text)
    assert "python" in skills
    assert "fastapi" in skills
    assert "postgresql" in skills


def test_extract_skills_case_insensitive():
    text = "Skilled in PYTHON and React."
    skills = extract_skills(text)
    assert "python" in skills
    assert "react" in skills


def test_extract_skills_no_match():
    text = "Experienced chef with culinary arts background."
    skills = extract_skills(text)
    assert skills == []


def test_extract_experience_years_standard_phrasing():
    text = "I have 5 years of experience in software development."
    assert extract_experience_years(text) == 5.0


def test_extract_experience_years_plus_notation():
    text = "Looking for candidates with 3+ years experience."
    assert extract_experience_years(text) == 3.0


def test_extract_experience_years_not_found():
    text = "Recent graduate looking for entry-level opportunities."
    assert extract_experience_years(text) is None
