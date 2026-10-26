import json

from src.generation.citations import format_citations
from src.generation.llm import generate_answer
from src.generation.prompt import build_context, build_conversation_prompt
from src.generation.query_rewriter import rewrite_query
from src.memory.conversation import ConversationMemory
from src.retrieval.retriever import Retriever


class RAGPipeline:

    def __init__(
        self,
        chunks_path="data/processed/chunks.json"
    ):

        print()
        print(
            "Loading document chunks..."
        )

        # =====================================================
        # LOAD CHUNKS
        # =====================================================

        with open(
            chunks_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.chunks = json.load(
                file
            )

        print(
            f"Loaded "
            f"{len(self.chunks)} "
            f"document chunks."
        )

        if not self.chunks:

            raise ValueError(
                "No document chunks found."
            )

        # =====================================================
        # INITIALIZE RETRIEVER
        # =====================================================

        self.retriever = Retriever(

            chunks=self.chunks,

            embedding_model=(
                "sentence-transformers/"
                "all-MiniLM-L6-v2"
            ),

            reranker_model=(
                "cross-encoder/"
                "ms-marco-MiniLM-L-6-v2"
            ),

            index_path=(
                "data/processed/"
                "faiss.index"
            )
        )

        # =====================================================
        # CONVERSATION MEMORY
        # =====================================================

        self.memory = ConversationMemory()

        print(
            "RAG pipeline initialized successfully."
        )

    # =========================================================
    # ASK QUESTION
    # =========================================================

    def ask(
        self,
        question,
        retrieval_k=10,
        top_k=3
    ):

        # =====================================================
        # VALIDATE QUESTION
        # =====================================================

        if not question:

            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        if not question:

            raise ValueError(
                "Question cannot be empty."
            )

        print()
        print(
            "=" * 60
        )

        print(
            f"QUESTION: {question}"
        )

        print(
            "=" * 60
        )

        # =====================================================
        # GET CONVERSATION HISTORY
        # =====================================================

        history = (
            self.memory.get_messages()
        )

        # =====================================================
        # QUERY REWRITING
        # =====================================================

        search_query = rewrite_query(
            question,
            history
        )

        print()
        print(
            "Search Query:"
        )

        print(
            search_query
        )

        # =====================================================
        # RETRIEVAL
        # =====================================================

        results = self.retriever.retrieve(

            query=search_query,

            retrieval_k=retrieval_k,

            top_k=top_k
        )

        # =====================================================
        # NO RELEVANT DOCUMENTS
        # =====================================================

        if not results:

            print()
            print(
                "No relevant documents found."
            )

            fallback_answer = (
                "The provided documents do not "
                "contain enough information to "
                "answer this question."
            )

            # Store conversation
            self.memory.add_message(
                "user",
                question
            )

            self.memory.add_message(
                "assistant",
                fallback_answer
            )

            return {

                "answer": fallback_answer,

                "citations": [],

                "results": [],

                "search_query": search_query
            }

        # =====================================================
        # BUILD DOCUMENT CONTEXT
        # =====================================================

        context = build_context(
            results,
            self.chunks
        )

        # =====================================================
        # BUILD LLM PROMPT
        # =====================================================

        prompt = build_conversation_prompt(

            question,

            context,

            history
        )

        # =====================================================
        # GENERATE ANSWER
        # =====================================================

        print()
        print(
            "Generating answer..."
        )

        answer = generate_answer(
            prompt
        )

        # =====================================================
        # CLEAN ANSWER
        # =====================================================

        if not answer:

            answer = (
                "The model did not return "
                "an answer."
            )

        answer = answer.strip()

        # =====================================================
        # UPDATE MEMORY
        # =====================================================

        self.memory.add_message(
            "user",
            question
        )

        self.memory.add_message(
            "assistant",
            answer
        )

        # =====================================================
        # FORMAT CITATIONS
        # =====================================================

        citations = format_citations(
            results,
            self.chunks
        )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        print()
        print(
            "Answer generated successfully."
        )

        print(
            f"Final citations: "
            f"{len(citations)}"
        )

        print(
            "=" * 60
        )

        return {

            "answer": answer,

            "citations": citations,

            "results": results,

            "search_query": search_query
        }

    # =========================================================
    # CLEAR CONVERSATION MEMORY
    # =========================================================

    def clear_memory(self):

        self.memory.clear()

        print(
            "Conversation memory cleared."
        )