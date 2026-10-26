import os

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer


class Retriever:

    def __init__(
        self,
        chunks,
        embedding_model,
        reranker_model,
        index_path="data/processed/faiss.index"
    ):
        self.chunks = chunks
        self.index_path = index_path

        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            embedding_model
        )

        print("Loading reranker model...")

        self.reranker = CrossEncoder(
            reranker_model
        )

        self._load_or_build_faiss()

        self._build_bm25()

        print("Retriever initialized successfully.")

    # =========================================================
    # FAISS
    # =========================================================

    def _load_or_build_faiss(self):

        if os.path.exists(self.index_path):

            print(
                f"Loading FAISS index from: "
                f"{self.index_path}"
            )

            self.faiss_index = faiss.read_index(
                self.index_path
            )

            print(
                "FAISS index loaded successfully."
            )

            print(
                f"Number of vectors: "
                f"{self.faiss_index.ntotal}"
            )

        else:

            print(
                "FAISS index not found."
            )

            print(
                "Creating FAISS index..."
            )

            self._build_faiss_index()

            index_directory = os.path.dirname(
                self.index_path
            )

            if index_directory:

                os.makedirs(
                    index_directory,
                    exist_ok=True
                )

            faiss.write_index(
                self.faiss_index,
                self.index_path
            )

            print(
                f"FAISS index saved to: "
                f"{self.index_path}"
            )

    # =========================================================
    # BUILD FAISS INDEX
    # =========================================================

    def _build_faiss_index(self):

        print(
            "Creating embeddings for all chunks..."
        )

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        if not texts:

            raise ValueError(
                "No document chunks available "
                "for embedding."
            )

        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        faiss.normalize_L2(
            embeddings
        )

        dimension = embeddings.shape[1]

        print(
            f"Embedding dimension: {dimension}"
        )

        self.faiss_index = faiss.IndexFlatIP(
            dimension
        )

        self.faiss_index.add(
            embeddings
        )

        print(
            f"Added "
            f"{self.faiss_index.ntotal} "
            f"vectors to FAISS."
        )

    # =========================================================
    # BM25
    # =========================================================

    def _build_bm25(self):

        print(
            "Building BM25 index..."
        )

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        tokenized_chunks = [
            text.lower().split()
            for text in texts
        ]

        self.bm25 = BM25Okapi(
            tokenized_chunks
        )

        print(
            "BM25 index built successfully."
        )

    # =========================================================
    # FAISS SEARCH
    # =========================================================

    def _faiss_search(
        self,
        query,
        top_k=10
    ):

        if self.faiss_index.ntotal == 0:

            return []

        # Never request more vectors than exist
        actual_k = min(
            top_k,
            self.faiss_index.ntotal
        )

        query_embedding = (
            self.embedding_model.encode(
                [query]
            )
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        faiss.normalize_L2(
            query_embedding
        )

        _, indices = (
            self.faiss_index.search(
                query_embedding,
                actual_k
            )
        )

        valid_indices = []

        for idx in indices[0].tolist():

            # FAISS can return -1 when
            # there are not enough vectors.
            if idx < 0:
                continue

            if idx >= len(self.chunks):
                continue

            valid_indices.append(idx)

        return valid_indices

    # =========================================================
    # BM25 SEARCH
    # =========================================================

    def _bm25_search(
        self,
        query,
        top_k=10
    ):

        if not self.chunks:

            return []

        query_tokens = (
            query.lower().split()
        )

        scores = self.bm25.get_scores(
            query_tokens
        )

        actual_k = min(
            top_k,
            len(scores)
        )

        top_indices = np.argsort(
            scores
        )[::-1][:actual_k]

        return [
            int(idx)
            for idx in top_indices
        ]

    # =========================================================
    # RECIPROCAL RANK FUSION
    # =========================================================

    def _rrf(
        self,
        result_lists,
        k=60
    ):

        scores = {}

        for result_list in result_lists:

            for rank, doc_id in enumerate(
                result_list,
                start=1
            ):

                if doc_id not in scores:

                    scores[doc_id] = 0

                scores[doc_id] += (
                    1 / (k + rank)
                )

        ranked_results = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked_results

    # =========================================================
    # CROSS ENCODER RERANKING
    # =========================================================

    def _rerank(
        self,
        query,
        candidate_indices,
        top_k=3,
        min_score=-5.0
    ):

        pairs = []
        valid_indices = []

        for idx in candidate_indices:

            if idx < 0:
                continue

            if idx >= len(self.chunks):
                continue

            pairs.append(
                [
                    query,
                    self.chunks[idx]["text"]
                ]
            )

            valid_indices.append(idx)

        if not pairs:

            return []

        print(
            f"Reranking "
            f"{len(pairs)} candidates..."
        )

        scores = self.reranker.predict(
            pairs
        )

        ranked = sorted(
            zip(
                valid_indices,
                scores
            ),
            key=lambda x: x[1],
            reverse=True
        )

        print(
            "Reranker scores:"
        )

        for idx, score in ranked:

            print(
                f"  Chunk {idx}: "
                f"{float(score):.4f}"
            )

        # Basic relevance filtering
        filtered = [
            item
            for item in ranked
            if float(item[1]) >= min_score
        ]

        print(
            f"Candidates after "
            f"relevance filtering: "
            f"{len(filtered)}"
        )

        return filtered[:top_k]

    # =========================================================
    # MAIN RETRIEVAL
    # =========================================================

    def retrieve(
        self,
        query,
        retrieval_k=10,
        top_k=3
    ):

        print()
        print(
            f"Retrieving documents for:"
            f" {query}"
        )

        # -----------------------------------------------------
        # FAISS
        # -----------------------------------------------------

        faiss_results = self._faiss_search(
            query,
            retrieval_k
        )

        print(
            f"FAISS results: "
            f"{len(faiss_results)}"
        )

        # -----------------------------------------------------
        # BM25
        # -----------------------------------------------------

        bm25_results = self._bm25_search(
            query,
            retrieval_k
        )

        print(
            f"BM25 results: "
            f"{len(bm25_results)}"
        )

        # -----------------------------------------------------
        # RRF
        # -----------------------------------------------------

        hybrid_results = self._rrf(
            [
                faiss_results,
                bm25_results
            ]
        )

        candidate_indices = [
            item[0]
            for item in hybrid_results[
                :retrieval_k
            ]
        ]

        print(
            f"Hybrid candidates: "
            f"{len(candidate_indices)}"
        )

        # -----------------------------------------------------
        # CROSS ENCODER
        # -----------------------------------------------------

        reranked_results = self._rerank(
            query,
            candidate_indices,
            top_k=top_k,
            min_score=-5.0
        )

        print(
            f"Retrieved "
            f"{len(reranked_results)} "
            f"final documents."
        )

        return reranked_results