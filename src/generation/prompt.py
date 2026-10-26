def build_context(results, chunks):
    
    context_blocks = []

    for i, item in enumerate(results, start=1):

        chunk_index = item[0]
        chunk = chunks[chunk_index]

        document = chunk.get(
            "document",
            "Unknown document"
        )

        page = chunk.get("page")

        # Handle PDF/DOCX/TXT
        if page is not None:
            location = f"Page: {page}"

        # Handle Excel
        elif chunk.get("sheet") is not None:
            location = (
                f"Sheet: {chunk['sheet']} | "
                f"Row: {chunk.get('row', 'N/A')}"
            )

        # Handle CSV
        elif chunk.get("row") is not None:
            location = f"Row: {chunk['row']}"

        else:
            location = "Location: Not available"

        context_blocks.append(
            f"""
[Source {i}]

Document: {document}
{location}

Content:
{chunk["text"]}
"""
        )

    return "\n".join(context_blocks)


def build_conversation_prompt(
    question,
    context,
    history
):

    history_text = ""

    for message in history:

        history_text += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n"
        )

    prompt = f"""
You are a document-based AI assistant.

Answer the user's question using ONLY the
information provided in the document context.

IMPORTANT RULES:

1. Give a direct and relevant answer.
2. Answer in ONLY 3 to 4 short sentences.
3. Do not repeat the question.
4. Do not add unnecessary background information.
5. Do not invent information.
6. Every factual statement must be supported
   by the provided context.
7. Add inline source references such as
   [Source 1] or [Source 2].
8. Only use source numbers that actually exist.
9. Place the source reference immediately after
   the statement it supports.
10. If the context does not contain enough
    information, say:

"The provided documents do not contain enough
information to answer this question."

Conversation History:
--------------------
{history_text}
--------------------

Document Context:
--------------------
{context}
--------------------

Question:
{question}

Answer in 3 to 4 short sentences with
inline citations:
"""

    return prompt


def build_prompt(question, context):

    prompt = f"""
You are a document-based AI assistant.

Answer the question using ONLY the provided context.

Rules:

- Give a direct and relevant answer.
- Use ONLY 3 to 4 short sentences.
- Do not repeat the question.
- Do not add unnecessary explanation.
- Do not invent information.
- Every factual statement must have
  a valid source citation.
- Use citations like [Source 1].
- Only use source numbers that exist.
- Place citations immediately after
  the relevant statement.
- If the answer is not available in the context,
  say that the provided documents do not contain
  enough information.

Context:
--------------------
{context}
--------------------

Question:
{question}

Answer in 3 to 4 short sentences:
"""

    return prompt