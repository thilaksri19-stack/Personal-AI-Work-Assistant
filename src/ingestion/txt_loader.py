import os


def load_txt(file_path):
    """
    Extract text from a TXT document.
    """

    document_name = os.path.basename(file_path)

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    return [
        {
            "document": document_name,
            "file_type": "txt",
            "page": None,
            "text": text
        }
    ]