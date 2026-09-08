import re


def clean_text(raw_text: str) -> str:
    """Normalize resume whitespace while preserving casing and punctuation."""
    cleaned_lines = []
    for line in raw_text.splitlines():
        normalized_line = re.sub(r"[ \t]+", " ", line.strip())
        if normalized_line:
            cleaned_lines.append(normalized_line)

    return "\n".join(cleaned_lines)
