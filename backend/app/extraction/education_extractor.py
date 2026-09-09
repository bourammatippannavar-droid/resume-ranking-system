import logging
import re

import spacy

logger = logging.getLogger(__name__)

_nlp = spacy.load("en_core_web_sm")

DEGREE_PATTERNS = [
    r"bachelor of (?:engineering|technology|science|arts|commerce)",
    r"master of (?:engineering|technology|science|arts|business administration)",
    r"\bb\.?\s?tech\b",
    r"\bm\.?\s?tech\b",
    r"\bb\.?\s?e\b",
    r"\bm\.?\s?e\b",
    r"\bb\.?\s?sc\b",
    r"\bm\.?\s?sc\b",
    r"\bmba\b",
    r"\bphd\b",
    r"\bdoctor of philosophy\b",
    r"\bdiploma in [a-z\s]+",
]

CERTIFICATION_KEYWORDS = [
    "aws certified", "azure certified", "google cloud certified",
    "pmp", "project management professional",
    "certified scrum master", "csm",
    "comptia", "ccna", "ccnp",
    "certified kubernetes", "cka", "ckad",
    "oracle certified", "microsoft certified",
    "six sigma", "itil",
]

INSTITUTION_KEYWORDS = ["university", "institute", "college", "school of", "polytechnic"]

PROXIMITY_WINDOW_CHARS = 150


def _is_valid_institution(entity_text: str) -> bool:
    """Require the entity to contain a real institution keyword, and reject multi-line noise."""
    if "\n" in entity_text:
        return False
    normalized = entity_text.strip().lower()
    if len(normalized) < 4:
        return False
    return any(keyword in normalized for keyword in INSTITUTION_KEYWORDS)


def extract_education(text: str) -> list[dict]:
    """Extract education entries: degree type (via regex) and nearby institution (via spaCy NER)."""
    text_lower = text.lower()
    degree_matches = []
    for pattern in DEGREE_PATTERNS:
        for match in re.finditer(pattern, text_lower):
            degree_matches.append((match.group(0).strip(), match.start(), match.end()))

    if not degree_matches:
        logger.info("No degree patterns found in text")
        return []

    doc = _nlp(text)
    org_entities = [
        (ent.text, ent.start_char, ent.end_char)
        for ent in doc.ents
        if ent.label_ == "ORG"
    ]

    education_entries = []
    for degree_text, start, end in degree_matches:
        nearby_institutions = [
            org_text for org_text, org_start, org_end in org_entities
            if abs(org_start - end) <= PROXIMITY_WINDOW_CHARS
            or abs(start - org_end) <= PROXIMITY_WINDOW_CHARS
        ]
        valid_institutions = [
            org for org in nearby_institutions if _is_valid_institution(org)
        ]
        education_entries.append({
            "degree": degree_text,
            "institutions": list(set(valid_institutions)),
        })

    logger.info("Extracted %d education entr(y/ies)", len(education_entries))
    return education_entries


def extract_certifications(text: str) -> list[str]:
    """Extract known certifications from resume text via keyword matching."""
    text_lower = text.lower()
    found = [cert for cert in CERTIFICATION_KEYWORDS if cert in text_lower]
    logger.info("Extracted %d certification(s)", len(found))
    return found
