import json
import sys
from pathlib import Path

from src.ingestion.chunker import create_document_chunks
from src.ingestion.document_loader import load_document
from src.ingestion.text_cleaner import clean_text

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks.json"
)


# ============================================================
# SUPPORTED FILES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


# ============================================================
# FIND DOCUMENTS
# ============================================================

def find_documents():

    documents = []

    for file_path in RAW_DIR.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() in (
            SUPPORTED_EXTENSIONS
        ):

            documents.append(file_path)

    return documents


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "📚 BioResearchLM Document Processor"
    )

    print("=" * 60)

    documents = find_documents()

    if not documents:

        print(
            "\n❌ No supported documents found."
        )

        print(
            "\nPut PDF, DOCX or TXT files inside:"
        )

        print(RAW_DIR)

        sys.exit(1)

    print(
        f"\nFound {len(documents)} document(s):"
    )

    for document in documents:

        print(
            f"  📄 {document.name}"
        )


    # --------------------------------------------------------
    # PROCESS ALL DOCUMENTS
    # --------------------------------------------------------

    all_chunks = []

    global_chunk_id = 0

    for file_path in documents:

        print("\n" + "-" * 60)

        print(
            f"Processing: {file_path.name}"
        )

        print("-" * 60)

        # Extract
        pages = load_document(
            str(file_path)
        )

        print(
            f"Extracted {len(pages)} sections"
        )

        # Clean
        cleaned_pages = []

        for page in pages:

            cleaned_text = clean_text(
                page["text"]
            )

            if not cleaned_text:
                continue

            cleaned_page = page.copy()

            cleaned_page["text"] = (
                cleaned_text
            )

            cleaned_pages.append(
                cleaned_page
            )

        print(
            f"Cleaned {len(cleaned_pages)} sections"
        )

        # Chunk
        chunks = create_document_chunks(
            cleaned_pages,
            chunk_size=500,
            overlap=100
        )

        # Reassign global IDs
        for chunk in chunks:

            chunk["chunk_id"] = (
                global_chunk_id
            )

            global_chunk_id += 1

            all_chunks.append(chunk)

        print(
            f"Created {len(chunks)} chunks"
        )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            ensure_ascii=False,
            indent=2
        )


    print("\n" + "=" * 60)

    print(
        f"✅ Total chunks: {len(all_chunks)}"
    )

    print(
        f"💾 Saved to: {OUTPUT_PATH}"
    )

    print("=" * 60)


if __name__ == "__main__":

    main()