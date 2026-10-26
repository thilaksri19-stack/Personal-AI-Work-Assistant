from flask import jsonify, render_template, request

from flask_app.services import (
    RAW_DIR,
    SUPPORTED_EXTENSIONS,
    clear_documents,
    delete_document,
    get_documents,
    process_documents,
)

# ============================================================
# RAG PIPELINE
# ============================================================

rag_pipeline = None


def get_rag_pipeline():

    global rag_pipeline

    if rag_pipeline is None:

        print()
        print("=" * 60)
        print("INITIALIZING RAG PIPELINE")
        print("=" * 60)

        from src.rag_pipeline import RAGPipeline

        rag_pipeline = RAGPipeline()

        print("RAG pipeline initialized.")
        print("=" * 60)

    return rag_pipeline


def reset_rag_pipeline():

    global rag_pipeline

    rag_pipeline = None

    print(
        "RAG pipeline reset."
    )


# ============================================================
# REGISTER ROUTES
# ============================================================

def register_routes(app):


    # ========================================================
    # HOME
    # ========================================================

    @app.route("/")
    def home():

        return render_template(
            "index.html"
        )


    # ========================================================
    # HEALTH
    # ========================================================

    @app.route("/health")
    def health():

        return jsonify({

            "success": True,

            "status": "running",

            "message":
                "Personal AI Assistant API is running."

        })


    # ========================================================
    # GET DOCUMENTS
    # ========================================================

    @app.route(
        "/documents",
        methods=["GET"]
    )
    def documents():

        try:

            document_list = (
                get_documents()
            )

            return jsonify({

                "success": True,

                "documents":
                    document_list,

                "count":
                    len(document_list)

            })

        except (FileNotFoundError, OSError, ValueError) as e:

            print(
                f"Documents error: {e}"
            )

            return jsonify({

                "success": False,

                "message":
                    str(e)

            }), 500


    # ========================================================
    # UPLOAD DOCUMENTS
    # ========================================================

    @app.route(
        "/upload",
        methods=["POST"]
    )
    def upload_documents():

        try:

            if "files" not in request.files:

                return jsonify({

                    "success": False,

                    "message":
                        "No files received."

                }), 400


            files = request.files.getlist(
                "files"
            )


            if not files:

                return jsonify({

                    "success": False,

                    "message":
                        "No files selected."

                }), 400


            uploaded_files = []


            # ------------------------------------------------
            # SAVE FILES
            # ------------------------------------------------

            for file in files:

                if (
                    not file
                    or not file.filename
                ):
                    continue


                filename = file.filename


                if "." not in filename:

                    return jsonify({

                        "success": False,

                        "message":
                            (
                                f"File has no "
                                f"extension: "
                                f"{filename}"
                            )

                    }), 400


                extension = (
                    "."
                    +
                    filename
                    .rsplit(".", 1)[1]
                    .lower()
                )


                if (
                    extension
                    not in SUPPORTED_EXTENSIONS
                ):

                    return jsonify({

                        "success": False,

                        "message":
                            (
                                f"Unsupported "
                                f"file type: "
                                f"{extension}"
                            )

                    }), 400


                from werkzeug.utils import secure_filename


                safe_filename = (
                    secure_filename(
                        filename
                    )
                )


                if not safe_filename:

                    return jsonify({

                        "success": False,

                        "message":
                            "Invalid filename."

                    }), 400


                file_path = (
                    RAW_DIR /
                    safe_filename
                )


                file.save(
                    str(file_path)
                )


                uploaded_files.append(
                    safe_filename
                )


                print(
                    f"Uploaded: "
                    f"{safe_filename}"
                )


            if not uploaded_files:

                return jsonify({

                    "success": False,

                    "message":
                        "No valid files uploaded."

                }), 400


            # ------------------------------------------------
            # PROCESS DOCUMENTS
            # ------------------------------------------------

            print()
            print("=" * 60)
            print(
                "PROCESSING DOCUMENTS"
            )
            print("=" * 60)


            processing_result = (
                process_documents()
            )


            if not processing_result[
                "success"
            ]:

                return jsonify({

                    "success": False,

                    "message":
                        "Document processing failed.",

                    "uploaded_files":
                        uploaded_files

                }), 500


            # ------------------------------------------------
            # IMPORTANT
            # Reset RAG pipeline
            # ------------------------------------------------

            reset_rag_pipeline()


            return jsonify({

                "success": True,

                "message":
                    (
                        "Documents uploaded "
                        "and processed successfully."
                    ),

                "uploaded_files":
                    uploaded_files,

                "document_count":
                    processing_result[
                        "document_count"
                    ],

                "chunk_count":
                    processing_result[
                        "chunk_count"
                    ]

            })


        except (OSError, ValueError, TypeError) as e:

            print()
            print(
                "UPLOAD ERROR:"
            )
            print(e)


            return jsonify({

                "success": False,

                "message":
                    str(e)

            }), 500


    # ========================================================
    # ASK RAG
    # ========================================================

    @app.route(
        "/ask",
        methods=["POST"]
    )
    def ask_question():

        try:

            # ------------------------------------------------
            # Read JSON
            # ------------------------------------------------

            data = request.get_json(
                silent=True
            )


            if not data:

                return jsonify({

                    "success": False,

                    "message":
                        "Request body is empty."

                }), 400


            question = data.get(
                "question",
                ""
            )


            question = question.strip()


            if not question:

                return jsonify({

                    "success": False,

                    "message":
                        "Question cannot be empty."

                }), 400


            # ------------------------------------------------
            # Check documents
            # ------------------------------------------------

            documents = get_documents()


            if not documents:

                return jsonify({

                    "success": False,

                    "message":
                        (
                            "No documents are "
                            "available. Please "
                            "upload a document first."
                        )

                }), 400


            # ------------------------------------------------
            # Get RAG pipeline
            # ------------------------------------------------

            pipeline = (
                get_rag_pipeline()
            )


            # ------------------------------------------------
            # Ask question
            # ------------------------------------------------

            print()
            print("=" * 60)
            print(
                f"QUESTION: {question}"
            )
            print("=" * 60)


            result = pipeline.ask(
                question
            )


            # ------------------------------------------------
            # Format citations
            # ------------------------------------------------

            citations = []


            for citation in result.get(
                "citations",
                []
            ):

                document = citation.get(
                    "document",
                    "Unknown document"
                )


                page = citation.get(
                    "page"
                )


                if page is not None:

                    source_text = (
                        f"{document} "
                        f"— Page {page}"
                    )

                else:

                    source_text = (
                        document
                    )


                citations.append(
                    source_text
                )


            # ------------------------------------------------
            # Return answer
            # ------------------------------------------------

            return jsonify({

                "success": True,

                "answer":
                    result.get(
                        "answer",
                        ""
                    ),

                "citations":
                    citations,

                "search_query":
                    result.get(
                        "search_query",
                        question
                    )

            })


        except (ValueError, TypeError, RuntimeError, OSError) as e:

            print()
            print("=" * 60)
            print("RAG ERROR")
            print("=" * 60)
            print(e)
            print("=" * 60)


            return jsonify({

                "success": False,

                "message":
                    str(e)

            }), 500


    # ========================================================
    # DELETE ONE DOCUMENT
    # ========================================================

    @app.route(
        "/documents/<path:filename>",
        methods=["DELETE"]
    )
    def remove_document(filename):

        try:

            result = (
                delete_document(
                    filename
                )
            )


            if not result[
                "success"
            ]:

                return jsonify(
                    result
                ), 404


            # Reset RAG pipeline
            reset_rag_pipeline()


            return jsonify(
                result
            )


        except (ValueError, TypeError, RuntimeError, OSError) as e:

            print(
                f"Delete error: {e}"
            )


            return jsonify({

                "success": False,

                "message":
                    str(e)

            }), 500


    # ========================================================
    # DELETE ALL DOCUMENTS
    # ========================================================

    @app.route(
        "/documents",
        methods=["DELETE"]
    )
    def remove_all_documents():

        try:

            result = (
                clear_documents()
            )


            # Reset RAG pipeline
            reset_rag_pipeline()


            return jsonify(
                result
            )


        except (ValueError, TypeError, RuntimeError, OSError) as e:

            print(
                f"Delete all error: {e}"
            )


            return jsonify({

                "success": False,

                "message":
                    str(e)

            }), 500