from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd
from docx import Document


def extract_text(file_path: str) -> str:
    """
    Extract plain text from PDF, DOCX, TXT, MD, XLSX
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _extract_pdf(path)

    elif ext == ".docx":
        return _extract_docx(path)

    elif ext in [".txt", ".md"]:
        return _extract_text_file(path)

    elif ext in [".xlsx", ".xls"]:
        return _extract_excel(path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(path: Path) -> str:
    text = []
    doc = fitz.open(path)
    for page in doc:
        text.append(page.get_text("text"))
    return "\n".join(text)


def _extract_docx(path: Path) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _extract_excel(path: Path) -> str:
    sheets = pd.read_excel(path, sheet_name=None)
    text = []

    for sheet_name, df in sheets.items():
        text.append(f"\n--- Sheet: {sheet_name} ---\n")
        text.append(df.astype(str).fillna("").to_string(index=False))

    return "\n".join(text)
