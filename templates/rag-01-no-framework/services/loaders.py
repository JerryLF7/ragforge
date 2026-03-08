import os

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup


def load_pdf(file_path: str) -> tuple[str, dict]:
    """Extract text from a PDF file."""
    doc = fitz.open(file_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    text = "\n".join(pages)
    return text, {
        "source_type": "pdf",
        "filename": os.path.basename(file_path),
    }


def load_text(file_path: str) -> tuple[str, dict]:
    """Read a text/markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return text, {
        "source_type": "text",
        "filename": os.path.basename(file_path),
    }


def load_url(url: str) -> tuple[str, dict]:
    """Fetch and extract text from a web page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; RAGBot/1.0)"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    title = soup.title.string if soup.title else url

    return text, {
        "source_type": "url",
        "filename": title,
        "url": url,
    }
