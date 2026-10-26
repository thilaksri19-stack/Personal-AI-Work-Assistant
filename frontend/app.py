import json
import sys
from pathlib import Path

import streamlit as st

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT PATHS
# ============================================================

RAW_DIR = PROJECT_ROOT / "data" / "raw"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CHUNKS_PATH = PROCESSED_DIR / "chunks.json"

FAISS_PATH = PROCESSED_DIR / "faiss.index"


# ============================================================
# IMPORTS
# ============================================================

from src.ingestion.chunker import create_document_chunks
from src.ingestion.document_loader import load_document
from src.ingestion.text_cleaner import clean_text
from src.rag_pipeline import RAGPipeline

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# DIRECTORIES
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
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


if "rag" not in st.session_state:
    st.session_state.rag = None


# ============================================================
# DOCUMENT PROCESSING
# ============================================================

def process_documents():

    documents = []

    supported_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    for file_path in RAW_DIR.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() in supported_extensions:

            documents.append(file_path)


    if not documents:

        return False, "No documents found."


    all_chunks = []

    global_chunk_id = 0


    # --------------------------------------------------------
    # PROCESS EACH DOCUMENT
    # --------------------------------------------------------

    for file_path in documents:

        try:

            pages = load_document(
                str(file_path)
            )

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


            chunks = create_document_chunks(
                cleaned_pages,
                chunk_size=500,
                overlap=100
            )


            # Assign global chunk IDs
            for chunk in chunks:

                chunk["chunk_id"] = (
                    global_chunk_id
                )

                global_chunk_id += 1

                all_chunks.append(chunk)


        except (OSError, RuntimeError, ValueError) as e:

            return (
                False,
                (
                    f"Error processing "
                    f"{file_path.name}: {e}"
                )
            )


    # --------------------------------------------------------
    # SAVE CHUNKS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # DELETE OLD FAISS INDEX
    # --------------------------------------------------------

    if FAISS_PATH.exists():

        FAISS_PATH.unlink()


    return (
        True,
        (
            f"Successfully processed "
            f"{len(documents)} document(s) "
            f"and created "
            f"{len(all_chunks)} chunks."
        )
    )


# ============================================================
# LOAD RAG
# ============================================================

@st.cache_resource
def create_rag_pipeline():

    return RAGPipeline()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🤖 Personal AI Work Assistant"
)

st.caption(
    "Chat with your documents using local RAG + Ollama"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "📚 Document Manager"
    )


    # --------------------------------------------------------
    # FILE UPLOADER
    # --------------------------------------------------------

    uploaded_files = st.file_uploader(
        "Upload your documents",
        type=[
            "pdf",
            "docx",
            "txt"
        ],
        accept_multiple_files=True
    )


    # --------------------------------------------------------
    # PROCESS BUTTON
    # --------------------------------------------------------

    if uploaded_files:

        st.write(
            f"📄 {len(uploaded_files)} "
            f"file(s) selected"
        )


        if st.button(
            "🔨 Process Documents",
            use_container_width=True
        ):

            with st.spinner(
                "Processing documents..."
            ):

                try:

                    # Save uploaded files
                    for uploaded_file in uploaded_files:

                        file_path = (
                            RAW_DIR
                            / uploaded_file.name
                        )

                        with open(
                            file_path,
                            "wb"
                        ) as file:

                            file.write(
                                uploaded_file.getbuffer()
                            )


                    # Process all documents
                    success, message = (
                        process_documents()
                    )


                    if success:

                        st.success(
                            message
                        )

                        # Clear cached RAG
                        create_rag_pipeline.clear()

                        st.session_state.rag = None

                        st.session_state.messages = []

                        st.rerun()

                    else:

                        st.error(
                            message
                        )


                except Exception as e:  # noqa: BLE001

                    st.error(
                        "❌ Document processing failed."
                    )

                    st.exception(e)


    st.divider()


    # --------------------------------------------------------
    # SHOW CURRENT DOCUMENTS
    # --------------------------------------------------------

    st.subheader(
        "📂 Current Documents"
    )


    supported_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }


    current_documents = [
        file_path
        for file_path in RAW_DIR.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower()
        in supported_extensions
    ]


    if current_documents:

        for file_path in current_documents:

            st.write(
                f"📄 {file_path.name}"
            )

    else:

        st.info(
            "No documents uploaded yet."
        )


    st.divider()


    # --------------------------------------------------------
    # CLEAR CONVERSATION
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        if st.session_state.rag:

            st.session_state.rag.clear_memory()

        st.session_state.messages = []

        st.rerun()


    # --------------------------------------------------------
    # REMOVE ALL DOCUMENTS
    # --------------------------------------------------------

    if st.button(
        "🧹 Remove All Documents",
        use_container_width=True
    ):

        for file_path in RAW_DIR.iterdir():

            if file_path.is_file():

                file_path.unlink()


        if CHUNKS_PATH.exists():

            CHUNKS_PATH.unlink()


        if FAISS_PATH.exists():

            FAISS_PATH.unlink()


        create_rag_pipeline.clear()

        st.session_state.rag = None

        st.session_state.messages = []

        st.success(
            "All documents removed."
        )

        st.rerun()


# ============================================================
# CHECK DOCUMENTS
# ============================================================

if not CHUNKS_PATH.exists():

    st.info(
        "👈 Upload documents from the sidebar "
        "and click **Process Documents**."
    )

    st.stop()


# ============================================================
# LOAD RAG PIPELINE
# ============================================================

if st.session_state.rag is None:

    with st.spinner(
        "Loading AI models..."
    ):

        try:

            st.session_state.rag = (
                create_rag_pipeline()
            )

        except Exception as e:  # noqa: BLE001

            st.error(
                "❌ Failed to load RAG pipeline."
            )

            st.exception(e)

            st.stop()


rag = st.session_state.rag


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask anything about your documents..."
)


# ============================================================
# QUESTION PROCESSING
# ============================================================

if question:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            question
        )


    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🔎 Searching your documents..."
        ):

            try:

                result = rag.ask(
                    question
                )

                answer = result[
                    "answer"
                ]

                citations = result[
                    "citations"
                ]

                search_query = result[
                    "search_query"
                ]


            except (KeyError, TypeError, ValueError, RuntimeError) as e:

                st.error(
                    "❌ Error while answering."
                )

                st.exception(e)

                st.stop()


        # ----------------------------------------------------
        # ANSWER
        # ----------------------------------------------------

        st.markdown(
            answer
        )


        # ----------------------------------------------------
        # SOURCES
        # ----------------------------------------------------

        if citations:

            st.markdown(
                "### 📚 Sources"
            )

            for citation in citations:

                source_number = citation[
                    "source"
                ]

                document = citation[
                    "document"
                ]

                page = citation[
                    "page"
                ]

                score = citation[
                    "score"
                ]


                if page is not None:

                    location = (
                        f"Page {page}"
                    )

                else:

                    location = (
                        "Document"
                    )


                st.write(
                    f"**[Source "
                    f"{source_number}]** "
                    f"{document} — "
                    f"{location} "
                    f"(Score: "
                    f"{score:.4f})"
                )


        # ----------------------------------------------------
        # RETRIEVAL DETAILS
        # ----------------------------------------------------

        with st.expander(
            "🔎 Retrieval Details"
        ):

            st.write(
                "### Search Query"
            )

            st.code(
                search_query
            )

            st.write(
                "### Sources Retrieved"
            )

            st.write(
                len(citations)
            )


    # --------------------------------------------------------
    # SAVE AI RESPONSE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )