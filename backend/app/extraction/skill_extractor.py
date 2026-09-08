import logging
import re

logger = logging.getLogger(__name__)

COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
    "sql", "postgresql", "mysql", "mongodb", "redis",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "git", "github", "ci/cd", "jenkins",
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow",
    "html", "css", "rest api", "graphql", "microservices",
    "agile", "scrum", "linux", "bash",
]


def extract_skills(text: str) -> list[str]:
    """Extract known technical skills from resume text via case-insensitive keyword matching."""
    text_lower = text.lower()
    found_skills = [skill for skill in COMMON_SKILLS if skill in text_lower]
    logger.info("Extracted %d skills from text", len(found_skills))
    return found_skills


def extract_experience_years(text: str) -> float | None:
    """Extract years of experience using common resume phrasing patterns."""
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*years?\s*(?:of\s*)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*years?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
    return None
