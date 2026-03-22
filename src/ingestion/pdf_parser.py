import fitz  # PyMuPDF
from src.utils import clean_text

def extract_text_from_pdf(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append({
            "page_number": page_num,
            "text": clean_text(text)
        })

    full_text = "\n\n".join(page["text"] for page in pages if page["text"].strip())

    return {
        "pdf_path": pdf_path,
        "num_pages": len(pages),
        "pages": pages,
        "full_text": clean_text(full_text)
    }