from src.rag_pipeline import RAGPipeline

rag = RAGPipeline()


# -------------------------
# Question 1
# -------------------------

question1 = "What is logistic regression?"

result1 = rag.ask(question1)

print("\nUSER:")
print(question1)

print("\nASSISTANT:")
print(result1["answer"])


# -------------------------
# Question 2
# -------------------------

question2 = "What are its advantages?"

result2 = rag.ask(question2)

print("\nUSER:")
print(question2)

print("\nSEARCH QUERY:")
print(result2["search_query"])

print("\nASSISTANT:")
print(result2["answer"])


# -------------------------
# Sources
# -------------------------

print("\nSOURCES:")

for citation in result2["citations"]:

    print(
        f"[Source {citation['source']}] "
        f"{citation['document']} - "
        f"Page {citation['page']}"
    )