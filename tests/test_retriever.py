import json

from src.retrieval.retriever import Retriever

with open(
    "data/processed/chunks.json",
    "r",
    encoding="utf-8"
) as file:

    chunks = json.load(file)


retriever = Retriever(
    chunks=chunks,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2"
)


query = "What is linear regression?"


results = retriever.retrieve(
    query,
    retrieval_k=20,
    top_k=5
)


print("\nTOP RESULTS\n")


for rank, (idx, score) in enumerate(
    results,
    start=1
):

    chunk = chunks[idx]

    print("=" * 70)

    print(f"Rank: {rank}")

    print(f"Chunk ID: {idx}")

    print(f"Score: {score}")

    print(f"Document: {chunk['document']}")

    print(f"Page: {chunk['page']}")

    print("\nText:")

    print(chunk["text"][:500])