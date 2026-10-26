from src.generation.llm import generate_answer


def rewrite_query(question, history):

    if not history:
        return question

    history_text = ""

    for message in history:

        history_text += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n"
        )

    prompt = f"""
You are a search query rewriting system.

Rewrite the user's current question into a
standalone search query that can be used to
retrieve relevant information from documents.

Use the conversation history to resolve references
such as:

- it
- its
- they
- this
- that
- these
- those

Rules:

1. Preserve the user's original meaning.
2. Do not answer the question.
3. Do not add information that is not present
   in the conversation.
4. Return ONLY the rewritten search query.
5. Keep the query concise.

Conversation History:
--------------------
{history_text}
--------------------

Current Question:
{question}

Standalone Search Query:
"""

    rewritten_query = generate_answer(prompt)

    return rewritten_query.strip()