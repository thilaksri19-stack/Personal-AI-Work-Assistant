import os

from src.ingestion.docx_loader import load_docx
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.txt_loader import load_txt

SUPPORTED_EXTENSIONS = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".txt": load_txt
}


def load_document(file_path):
    """
    Automatically detect the document type
    and load the document.
    """

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    loader = SUPPORTED_EXTENSIONS[
        extension
    ]

    return loader(file_path)