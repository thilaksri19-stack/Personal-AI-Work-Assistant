import os

from docx import Document


def load_docx(file_path):
    """
    Extract text from a DOCX document.
    """

    document = Document(file_path)

    document_name = os.path.basename(file_path)

    pages = []

    for paragraph_number, paragraph in enumerate(
        document.paragraphs,
        start=1
    ):

        text = paragraph.text.strip()

        if not text:
            continue

        pages.append({
            "document": document_name,
            "file_type": "docx",
            "page": None,
            "paragraph": paragraph_number,
            "text": text
        })

    return pages