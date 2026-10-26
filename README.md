# Personal AI Work Assistant — Multi-Document RAG

A local, document-grounded AI assistant that lets users upload work and learning documents, ask questions in natural language, and receive concise answers with source references.

The project combines **hybrid retrieval**, **cross-encoder reranking**, a **local LLM**, and a **Flask web application**. It is designed as a learning and portfolio project for understanding how a Retrieval-Augmented Generation (RAG) system works end to end.

> **Project status:** Core ingestion, retrieval, local generation, conversation memory, and Flask UI have been implemented. Continue validating answer grounding, citation accuracy, and performance with your own test documents.

---

## Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Supported Files](#supported-files)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run the Application](#run-the-application)
- [How the RAG Pipeline Works](#how-the-rag-pipeline-works)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Testing](#testing)
- [Performance Notes](#performance-notes)
- [Troubleshooting](#troubleshooting)
- [Security and Privacy](#security-and-privacy)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Learning Outcomes](#learning-outcomes)
- [License](#license)

---

## Overview

Personal AI Work Assistant is a local-first application for asking questions about a collection of documents. Instead of relying only on an LLM's general knowledge, the application retrieves potentially relevant passages from uploaded files and supplies them as context for answer generation.

Typical use cases include:

- Asking questions about study notes and technical documentation.
- Finding information across multiple work documents.
- Summarizing relevant passages from PDFs and text files.
- Searching structured CSV and Excel data using natural-language questions.
- Exploring a practical implementation of a hybrid RAG pipeline.

The application currently uses **Ollama with `llama3.2:3b`** for local answer generation. Embedding and reranking models are loaded through Sentence Transformers.

## Features

- **Multi-document upload:** Upload supported documents through the web interface.
- **Document extraction:** Extract text from PDFs, Word documents, text files, CSV files, and Excel workbooks.
- **Text cleaning and chunking:** Clean extracted text and split it into smaller retrieval units.
- **Semantic retrieval:** Use `sentence-transformers/all-MiniLM-L6-v2` embeddings with FAISS.
- **Keyword retrieval:** Use BM25 to find passages containing query terms.
- **Hybrid ranking:** Combine semantic and keyword rankings using Reciprocal Rank Fusion (RRF).
- **Reranking:** Use `cross-encoder/ms-marco-MiniLM-L-6-v2` to rerank candidate passages.
- **Local answer generation:** Generate answers with Ollama and `llama3.2:3b`.
- **Conversation memory:** Retain a limited conversation history for follow-up questions.
- **Source metadata:** Return document and available page/sheet/row information for retrieved content.
- **Web interface:** Use a responsive HTML, CSS, and JavaScript interface served by Flask.
- **Document management:** View uploaded documents, upload more files, and delete individual or all supported documents.
- **JSON API:** Flask endpoints connect the frontend to ingestion and question-answering services.

## Architecture

```text
User
 │
 ▼
HTML / CSS / JavaScript
 │ HTTP requests
 ▼
Flask application
 ├── Document upload and management
 └── Question-answering API
          │
          ▼
      RAG pipeline
          │
          ├── Query rewriting (when conversation history exists)
          │
          ├── FAISS semantic search
          │
          ├── BM25 keyword search
          │
          ├── Reciprocal Rank Fusion (RRF)
          │
          ├── Cross-encoder reranking
          │
          ├── Context builder with source metadata
          │
          └── Ollama / Llama 3.2 3B
                    │
                    ▼
          Answer + citation metadata
                    │
                    ▼
              Flask JSON response
                    │
                    ▼
                Web interface
```

### Ingestion and indexing

```text
Uploaded files
     │
     ▼
File-type-specific loaders
     │
     ▼
Text cleaning
     │
     ▼
Chunking
     │
     ├── chunks.json (text + metadata)
     │
     └── Embedding model
              │
              ▼
          FAISS index
```

BM25 is built from the loaded chunks when the retriever initializes. FAISS stores dense vectors; `chunks.json` stores the associated text and metadata.

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Language | Python | Application and RAG logic |
| Web backend | Flask | Routes and HTTP API |
| Frontend | HTML, CSS, JavaScript | Chat and document-management UI |
| PDF extraction | PyMuPDF | Extract text from PDF pages |
| DOCX extraction | Python document parser in `docx_loader.py` | Extract Word document text |
| Tabular data | Pandas | Read CSV and Excel data |
| Embeddings | Sentence Transformers | Convert text and queries to vectors |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | 384-dimensional text embeddings |
| Vector search | FAISS | Similarity search over embeddings |
| Keyword search | `rank-bm25` | Lexical retrieval |
| Hybrid fusion | Reciprocal Rank Fusion | Combine retrieval rankings |
| Reranking | Sentence Transformers CrossEncoder | Rerank candidate passages |
| Reranker model | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Query–passage relevance scoring |
| Local LLM runtime | Ollama | Run the generation model locally |
| Generation model | `llama3.2:3b` | Generate context-grounded responses |

## Supported Files

The current ingestion registry supports:

| Extension | Description |
|---|---|
| `.pdf` | PDF documents |
| `.docx` | Microsoft Word documents |
| `.txt` | Plain-text files |
| `.csv` | Comma-separated tabular data |
| `.xlsx` | Excel workbooks |

Support depends on the corresponding loader being installed and correctly configured. Scanned PDFs may require OCR; the current text extraction path does not guarantee OCR support. Legacy `.doc` files and other formats are not included in the current registry.

## Project Structure

```text
Bioreasearch_LM_Project/
├── data/
│   ├── raw/                       # Uploaded source files
│   └── processed/
│       ├── chunks.json            # Extracted chunks and metadata
│       └── faiss.index            # FAISS vector index
├── src/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   ├── docx_loader.py
│   │   ├── txt_loader.py
│   │   ├── table_loader.py
│   │   ├── document_loader.py
│   │   ├── text_cleaner.py
│   │   ├── chunker.py
│   │   └── build_chunks.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedder.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── retriever.py
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── prompt.py
│   │   ├── llm.py
│   │   ├── citations.py
│   │   └── query_rewriter.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── conversation.py
│   └── rag_pipeline.py
├── flask_app/
│   ├── __init__.py
│   ├── app.py
│   ├── routes.py
│   └── services.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── tests/
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

Some optional modules may change as the project evolves. Keep the README aligned with the files actually present in your repository.

## Requirements

- Windows, macOS, or Linux (the setup below uses Windows PowerShell).
- Python 3.10 or a compatible Python version for the installed package set.
- Ollama installed and running.
- Internet access for the initial download of embedding/reranker model files, unless they are already cached.
- Enough RAM and disk space for the Python packages, models, document chunks, and indexes.

### Main Python dependencies

Your `requirements.txt` should include the packages needed by the loaders, retrieval pipeline, and Flask application. For example:

```text
Flask
flask-cors
pymupdf
python-docx
pandas
openpyxl
sentence-transformers
faiss-cpu
rank-bm25
numpy
scikit-learn
ollama
python-dotenv
```

Use the project’s actual `requirements.txt` as the source of truth. Avoid blindly adding every package listed here if the code does not use it. Install compatible versions together in your active virtual environment.

## Installation

### 1. Clone the repository

Replace the placeholder with your repository URL:

```powershell
git clone <YOUR_REPOSITORY_URL>
cd Bioreasearch_LM_Project
```

Or open your existing project directory in VS Code.

### 2. Create and activate a virtual environment

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the appropriate execution policy approved for your machine, or run the virtual environment's Python executable directly. Do not weaken organizational security controls without authorization.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If installation or imports fail because Windows Application Control blocks a native DLL, do not try to bypass that policy. Check the blocked module and consult your administrator or device support team.

### 4. Install and prepare Ollama

Install Ollama from its official website: https://ollama.com/

Pull the model used by this project:

```powershell
ollama pull llama3.2:3b
```

Check that the model is available:

```powershell
ollama list
```

Test it:

```powershell
ollama run llama3.2:3b
```

Enter a short test prompt, then exit the interactive session. Ensure the Ollama service is running when you start the Flask application.

### 5. Prepare the data directories

Ensure these directories exist:

```text
data/raw/
data/processed/
```

The Flask upload service can populate `data/raw/`. Processed chunks and the FAISS index are stored under `data/processed/`.

## Run the Application

From the project root, with the virtual environment activated:

```powershell
python flask_app/app.py
```

Open the local address printed in the terminal:

```text
http://127.0.0.1:5000
```

Health endpoint:

```text
http://127.0.0.1:5000/health
```

### First use

1. Open the web interface.
2. Upload one or more supported documents.
3. Wait for extraction, cleaning, chunking, and indexing to complete.
4. Ask a question that the documents can answer.
5. Review the answer and the source information shown by the UI.
6. Try a question that is unrelated to the documents to evaluate grounding behavior.

The first question after a fresh index may take longer because the embedding and reranking models must load. Initial indexing can also take time on a CPU-only machine. Subsequent queries should reuse the saved FAISS index when it is valid.

## How the RAG Pipeline Works

### 1. Document ingestion

A loader selected by file extension extracts text and metadata from each supported file. PDF pages and table rows may carry different metadata fields.

### 2. Cleaning and chunking

Text is normalized and split into smaller chunks. Chunk size and overlap affect retrieval quality, context length, and processing cost. A chunk that is too large can contain unrelated information; a chunk that is too small can lose context.

### 3. Embedding generation

`all-MiniLM-L6-v2` converts each chunk into a dense vector. The query is embedded with the same model so it can be compared with indexed document vectors.

### 4. FAISS semantic search

FAISS searches for vectors similar to the query vector. The current design uses normalized embeddings and an inner-product index to approximate cosine similarity.

### 5. BM25 keyword search

BM25 ranks chunks based on lexical term overlap. This can help when queries contain exact terms, names, or technical vocabulary.

### 6. Reciprocal Rank Fusion

RRF combines the ranked results from FAISS and BM25. It uses the ranks of chunks in the result lists rather than directly comparing their raw scores.

### 7. Cross-encoder reranking

A CrossEncoder scores each candidate using both the query and the candidate passage. This is more computationally expensive than vector search, so the application reranks a limited set of candidates.

### 8. Context construction

The highest-ranked passages are assembled into a prompt with source identifiers and available document-location metadata.

### 9. Local answer generation

Ollama runs `llama3.2:3b` to generate an answer using the supplied context and instructions. The prompt asks for a concise response and source references.

### 10. Conversation memory

A bounded in-memory history is used for follow-up questions and query rewriting. This memory is process-local; it is not a persistent database and may be lost when the server restarts.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serve the web interface |
| `GET` | `/health` | Check whether the API is running |
| `GET` | `/documents` | List uploaded supported documents |
| `POST` | `/upload` | Upload and process documents |
| `POST` | `/ask` | Submit a question and receive an answer |
| `DELETE` | `/documents/<filename>` | Delete one document |
| `DELETE` | `/documents` | Delete all supported documents |

### Example question request

```http
POST /ask
Content-Type: application/json
```

```json
{
  "question": "What is deep learning?"
}
```

A successful response is expected to follow this general shape:

```json
{
  "success": true,
  "answer": "An answer based on the retrieved document context. [Source 1]",
  "citations": [
    {
      "source": 1,
      "text": "example.pdf — Page 4"
    }
  ],
  "search_query": "What is deep learning?"
}
```

The exact response fields depend on the current implementation. A citation is useful only when its source identifier corresponds to the context used to generate the answer; verify this behavior during testing.

## Configuration

The current model names are configured in the Python source:

- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Ollama model: `llama3.2:3b`

Retrieval defaults in the current pipeline are designed to search a limited candidate set and rerank a smaller number of passages. Tune them against a small, representative evaluation set rather than assuming one setting is best for every dataset.

If you use a `.env` file for future configuration, do not commit API keys, passwords, or other secrets. The current local Ollama flow does not require an OpenAI API key.

## Testing

Before calling the project complete, test:

1. A question with a clear answer in a PDF.
2. A question requiring information from another supported file type.
3. A follow-up question that refers to an earlier question.
4. A question whose answer is absent from the uploaded documents.
5. An empty question.
6. Uploading an unsupported file type.
7. Deleting one document and checking that the remaining documents are still searchable.
8. Deleting all documents and confirming that the app handles an empty corpus safely.
9. Restarting the application and verifying that an existing, valid FAISS index loads correctly.
10. Checking that every displayed citation points to a retrieved source and the correct page/sheet/row where available.

For repeatable evaluation, maintain a small test set containing questions, expected supporting documents, and notes about whether the generated answer is adequately supported.

## Performance Notes

- The initial model download and first index build can take a while.
- On CPU-only systems, embedding thousands of chunks and reranking candidates can be slow.
- Reuse a valid FAISS index instead of recomputing all embeddings on every application start.
- Keep the number of reranking candidates modest while evaluating retrieval quality.
- Limit the amount of context passed to the LLM.
- Streaming can improve perceived responsiveness by displaying generated text as it arrives.
- Query rewriting may add an extra LLM call for follow-up questions.
- Measure query rewriting, retrieval, reranking, context construction, and generation separately before optimizing.

## Troubleshooting

### The `/ask` endpoint returns HTTP 500

Read the Flask terminal traceback. Test the dependencies separately to identify which import or runtime component fails.

### A native DLL is blocked on Windows

If the error says that an Application Control policy blocked a DLL, this is a Windows security-policy issue. Do not attempt to evade the policy. Identify the blocked dependency and ask the device administrator or support team for an approved resolution.

### Ollama cannot find the model

Check the available models:

```powershell
ollama list
```

If needed, pull the configured model:

```powershell
ollama pull llama3.2:3b
```

Confirm the Ollama service is running.

### Answers are slow

Use timing logs to separate model generation from query rewriting, retrieval, and reranking. A slow first query may include model loading; a fresh index may also require embedding every chunk.

### Answers are unrelated or poorly supported

Check the retrieved passages and reranker scores, not just the final generated answer. Improve chunking and retrieval, validate citations, and add an evidence/grounding evaluation layer. A reranker score threshold is model-dependent and should not be treated as a universal confidence probability.

### FAISS index does not match chunks

The FAISS index and `chunks.json` must represent the same chunk collection in the same order. If documents are reprocessed or chunk order changes, rebuild the index through the application's indexing flow. Do not reuse a stale index against different chunks.

## Security and Privacy

- The intended generation flow uses a local Ollama model.
- Uploaded documents are stored in the local `data/raw/` directory unless you change the storage implementation.
- Keep `.env`, private documents, generated indexes, and other sensitive files out of public repositories unless you explicitly intend to publish them.
- Validate upload file types and sizes; extension checks alone do not guarantee that a file is safe.
- This project is a learning application, not a hardened multi-user production service.
- The Flask development server is suitable for local development only. Use an appropriate production WSGI server and review deployment security before exposing the app to a network.
- Do not upload copyrighted or confidential documents to a public repository. Use documents you own or are licensed to use.

## Limitations and Future Improvements

- **Grounding and abstention:** Add and evaluate a robust evidence check so unsupported questions are answered with a clear “not enough information” response.
- **Citation validation:** Validate inline source identifiers against the actual context and align them with displayed citation metadata.
- **Streaming responses:** Stream LLM tokens to the browser to improve perceived latency.
- **Incremental indexing:** Embed and add only newly uploaded documents rather than rebuilding the complete index.
- **Persistent conversation storage:** Store sessions in a database if conversations must survive restarts.
- **Improved table retrieval:** Use row-aware chunking and metadata filters for CSV and Excel files.
- **Scanned PDF support:** Add OCR when scanned documents need to be searchable.
- **Evaluation:** Track retrieval metrics such as Recall@k and answer quality/groundedness on a curated test set.
- **Observability:** Add structured logging, latency measurements, and clearer error messages.
- **Production readiness:** Add authentication, request validation, upload hardening, and deployment configuration.
- **Automated tests:** Add unit and integration tests for loaders, retrieval, routes, and document lifecycle operations.

## Learning Outcomes

This project provides practical experience with:

- Building a modular Python application.
- Creating a multi-format document ingestion pipeline.
- Chunking and embedding text.
- Implementing vector search with FAISS.
- Implementing keyword retrieval with BM25.
- Combining retrievers with Reciprocal Rank Fusion.
- Reranking with a CrossEncoder.
- Connecting a local LLM through Ollama.
- Building REST endpoints with Flask.
- Connecting a JavaScript frontend to a Python backend.
- Managing conversation context and source metadata.
- Debugging ML dependencies and measuring pipeline latency.

## License

Add a `LICENSE` file before publishing the repository. Choose a license that matches your intended use and the rights you have to distribute the code. Ensure that any sample documents, datasets, model assets, and third-party materials are separately licensed for the way you use them.

---

**Built as an end-to-end RAG learning and portfolio project.**
