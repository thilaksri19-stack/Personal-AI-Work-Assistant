def create_document_chunks(
    pages,
    chunk_size=500,
    overlap=100
):
    """
    Convert extracted document sections
    into overlapping chunks.
    """

    all_chunks = []

    chunk_id = 0

    for page in pages:

        text = page["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            if chunk_text.strip():

                chunk = {
                    "chunk_id": chunk_id,
                    "document": page["document"],
                    "file_type": page["file_type"],
                    "page": page.get("page"),
                    "text": chunk_text
                }

                # Preserve paragraph information
                # if available.
                if "paragraph" in page:

                    chunk["paragraph"] = (
                        page["paragraph"]
                    )

                all_chunks.append(chunk)

                chunk_id += 1

            start = end - overlap

    return all_chunks