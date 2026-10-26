from src.ingestion.pdf_loader import load_pdf

pdf_path = "data/raw/Data Science.pdf"

pages = load_pdf(pdf_path)

print("Number of pages:", len(pages))

for page in pages[:2]:
    print("\nPage:", page["page"])
    print(page["text"][:500])