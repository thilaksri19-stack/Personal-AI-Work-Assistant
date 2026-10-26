from src.generation.query_rewriter import rewrite_query

history = [
    {
        "role": "user",
        "content": "What is logistic regression?"
    },
    {
        "role": "assistant",
        "content": "Logistic regression is a classification method."
    }
]


question = "What are its advantages?"


rewritten = rewrite_query(
    question,
    history
)


print("\nOriginal question:")
print(question)

print("\nRewritten query:")
print(rewritten)