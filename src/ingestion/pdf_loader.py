import os

import pymupdf


def load_pdf(file_path):
    """
    Extract text from a PDF page by page.
    """

    document = pymupdf.open(file_path)

    pages = []

    document_name = os.path.basename(file_path)

    for page_number, page in enumerate(
        document,
        start=1
    ):

        text = page.get_text()

        pages.append({
            "document": document_name,
            "file_type": "pdf",
            "page": page_number,
            "text": text
        })

    document.close()

    return pages