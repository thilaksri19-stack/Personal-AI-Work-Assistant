def format_citations(results, chunks):
    
    citations = []
    seen = set()

    for rank, (idx, score) in enumerate(
        results,
        start=1
    ):

        if idx < 0 or idx >= len(chunks):
            continue

        chunk = chunks[idx]

        document = chunk.get(
            "document",
            "Unknown document"
        )

        page = chunk.get("page")
        sheet = chunk.get("sheet")
        row = chunk.get("row")

        # Avoid duplicate sources
        key = (
            document,
            page,
            sheet,
            row
        )

        if key in seen:
            continue

        seen.add(key)

        citation = {
            "source": rank,
            "document": document,
            "score": float(score)
        }

        if page is not None:
            citation["page"] = page

        if sheet is not None:
            citation["sheet"] = sheet

        if row is not None:
            citation["row"] = row

        citations.append(citation)

    return citations