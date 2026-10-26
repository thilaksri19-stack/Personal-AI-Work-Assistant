from src.rag_pipeline import RAGPipeline


print("Initializing RAG pipeline...")


rag = RAGPipeline()


question = "What is decision tree?"


print("\nQuestion:")
print(question)


result = rag.ask(question)


print("\n" + "=" * 70)
print("ANSWER")
print("=" * 70)

print(result["answer"])

print("\n" + "=" * 70)
print("SOURCES")
print("=" * 70)

for citation in result["citations"]:

    print(
        f"[Source {citation['source']}] "
        f"{citation['document']} "
        f"- Page {citation['page']}"
    )


print("\n" + "=" * 70)
print("RETRIEVED SOURCES")
print("=" * 70)


for rank, (idx, score) in enumerate(
    result["results"],
    start=1
):

    chunk = rag.chunks[idx]

    print(
        f"\nSource {rank}"
    )

    print(
        f"Document: {chunk['document']}"
    )

    print(
        f"Page: {chunk['page']}"
    )

    print(
        f"Reranker Score: {score}"
    )