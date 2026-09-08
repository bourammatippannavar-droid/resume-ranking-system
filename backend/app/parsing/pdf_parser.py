import logging

import pymupdf as fitz


logger = logging.getLogger(__name__)


class PDFParsingError(Exception):
    """Raised when a PDF cannot be opened or parsed."""


def extract_text_from_pdf(file_path: str) -> str:
    try:
        with fitz.open(file_path) as document:
            page_text = [page.get_text() for page in document]
            logger.info("Processed %d PDF pages from %s", len(page_text), file_path)
            return "\n".join(page_text)
    except Exception as exc:
        logger.error("Failed to parse PDF %s: %s", file_path, exc)
        raise PDFParsingError(f"Unable to parse PDF file: {file_path}") from exc
