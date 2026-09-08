import logging

import docx


logger = logging.getLogger(__name__)


class DOCXParsingError(Exception):
    """Raised when a DOCX file cannot be opened or parsed."""


def extract_text_from_docx(file_path: str) -> str:
    try:
        document = docx.Document(file_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        logger.info(
            "Processed %d DOCX paragraphs from %s",
            len(paragraphs),
            file_path,
        )
        return "\n".join(paragraphs)
    except Exception as exc:
        logger.error("Failed to parse DOCX %s: %s", file_path, exc)
        raise DOCXParsingError(f"Unable to parse DOCX file: {file_path}") from exc
