import json
from pathlib import Path

from src.ingestion.document_loader import load_document
from src.ingestion.text_cleaner import clean_text
from src.ingestion.chunker import create_document_chunks


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"

PROCESSED_DIR = (
    PROJECT_ROOT /
    "data" /
    "processed"
)

CHUNKS_PATH = (
    PROCESSED_DIR /
    "chunks.json"
)

FAISS_PATH = (
    PROCESSED_DIR /
    "faiss.index"
)


# ============================================================
# SUPPORTED DOCUMENT TYPES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".csv",
    ".xlsx"
}


# ============================================================
# CREATE DIRECTORIES
# ============================================================

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

def get_documents():

    documents = []

    for file_path in RAW_DIR.iterdir():

        if not file_path.is_file():
            continue

        if (
            file_path.suffix.lower()
            not in SUPPORTED_EXTENSIONS
        ):
            continue

        documents.append({

            "name":
                file_path.name,

            "type":
                file_path.suffix
                .lower()
                .replace(".", ""),

            "size":
                file_path.stat().st_size

        })

    # Sort alphabetically
    documents.sort(
        key=lambda x: x["name"].lower()
    )

    return documents


# ============================================================
# PROCESS ALL DOCUMENTS
# ============================================================

def process_documents():

    documents = []

    for file_path in RAW_DIR.iterdir():

        if not file_path.is_file():
            continue

        if (
            file_path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        ):
            documents.append(file_path)


    # --------------------------------------------------------
    # No documents
    # --------------------------------------------------------

    if not documents:

        # Remove old chunks
        if CHUNKS_PATH.exists():
            CHUNKS_PATH.unlink()

        # Remove old FAISS index
        if FAISS_PATH.exists():
            FAISS_PATH.unlink()

        return {

            "success": True,

            "message":
                "No documents available.",

            "document_count":
                0,

            "chunk_count":
                0

        }


    # --------------------------------------------------------
    # Process documents
    # --------------------------------------------------------

    all_chunks = []

    global_chunk_id = 0


    for file_path in documents:

        print()
        print("=" * 60)

        print(
            f"Processing: {file_path.name}"
        )

        print("=" * 60)


        # ----------------------------------------------------
        # Load document
        # ----------------------------------------------------

        pages = load_document(
            str(file_path)
        )

        print(
            f"Extracted sections: "
            f"{len(pages)}"
        )


        # ----------------------------------------------------
        # Clean text
        # ----------------------------------------------------

        cleaned_pages = []


        for page in pages:

            raw_text = page.get(
                "text",
                ""
            )

            cleaned_text = clean_text(
                raw_text
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
            f"Valid sections: "
            f"{len(cleaned_pages)}"
        )


        # ----------------------------------------------------
        # Create chunks
        # ----------------------------------------------------

        chunks = create_document_chunks(

            cleaned_pages,

            chunk_size=500,

            overlap=100

        )


        print(
            f"Created chunks: "
            f"{len(chunks)}"
        )


        # ----------------------------------------------------
        # Assign global chunk IDs
        # ----------------------------------------------------

        for chunk in chunks:

            chunk["chunk_id"] = (
                global_chunk_id
            )

            global_chunk_id += 1

            all_chunks.append(
                chunk
            )


    # ========================================================
    # SAVE CHUNKS
    # ========================================================

    with open(
        CHUNKS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            all_chunks,

            file,

            ensure_ascii=False,

            indent=2

        )


    print()
    print("=" * 60)

    print(
        f"Total documents: "
        f"{len(documents)}"
    )

    print(
        f"Total chunks: "
        f"{len(all_chunks)}"
    )

    print("=" * 60)


    # ========================================================
    # DELETE OLD FAISS INDEX
    # ========================================================

    if FAISS_PATH.exists():

        FAISS_PATH.unlink()

        print(
            "Old FAISS index deleted."
        )


    return {

        "success": True,

        "message":
            (
                f"Processed "
                f"{len(documents)} "
                f"document(s) successfully."
            ),

        "document_count":
            len(documents),

        "chunk_count":
            len(all_chunks)

    }


# ============================================================
# DELETE ONE DOCUMENT
# ============================================================

def delete_document(filename):

    # Prevent path traversal
    safe_filename = Path(
        filename
    ).name


    file_path = (
        RAW_DIR /
        safe_filename
    )


    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not file_path.exists():

        return {

            "success": False,

            "message":
                "Document not found."

        }


    if not file_path.is_file():

        return {

            "success": False,

            "message":
                "Invalid document."

        }


    # --------------------------------------------------------
    # Delete file
    # --------------------------------------------------------

    file_path.unlink()


    print()
    print(
        f"Deleted document: "
        f"{safe_filename}"
    )


    # --------------------------------------------------------
    # Reprocess remaining documents
    # --------------------------------------------------------

    result = process_documents()


    return {

        "success": True,

        "message":
            (
                f"{safe_filename} "
                f"deleted successfully."
            ),

        "reindex":
            result

    }


# ============================================================
# DELETE ALL DOCUMENTS
# ============================================================

def clear_documents():

    deleted_count = 0


    # --------------------------------------------------------
    # Delete raw documents
    # --------------------------------------------------------

    for file_path in RAW_DIR.iterdir():

        if not file_path.is_file():
            continue

        if (
            file_path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        ):

            file_path.unlink()

            deleted_count += 1


    # --------------------------------------------------------
    # Delete processed chunks
    # --------------------------------------------------------

    if CHUNKS_PATH.exists():

        CHUNKS_PATH.unlink()


    # --------------------------------------------------------
    # Delete FAISS index
    # --------------------------------------------------------

    if FAISS_PATH.exists():

        FAISS_PATH.unlink()


    print()
    print(
        f"Deleted {deleted_count} "
        f"document(s)."
    )


    return {

        "success": True,

        "message":
            (
                f"Deleted "
                f"{deleted_count} "
                f"document(s) successfully."
            ),

        "deleted_count":
            deleted_count

    }