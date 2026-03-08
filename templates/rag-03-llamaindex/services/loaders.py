import os
from pathlib import Path

from llama_index.core import Document
from llama_index.readers.file import PyMuPDFReader
from llama_index.readers.web import SimpleWebPageReader


def load_pdf(file_path: str) -> tuple[list[Document], dict]:
    """Load PDF using LlamaIndex PyMuPDFReader."""
    reader = PyMuPDFReader()
    docs = reader.load_data(file_path=Path(file_path))
    metadata = {
        "source_type": "pdf",
        "filename": os.path.basename(file_path),
    }
    return docs, metadata


def load_text(file_path: str) -> tuple[list[Document], dict]:
    """Load text/markdown as a LlamaIndex Document."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    metadata = {
        "source_type": "text",
        "filename": os.path.basename(file_path),
    }
    docs = [Document(text=text, metadata=metadata)]
    return docs, metadata


def load_url(url: str) -> tuple[list[Document], dict]:
    """Load web page using LlamaIndex SimpleWebPageReader."""
    reader = SimpleWebPageReader(html_to_text=True)
    docs = reader.load_data(urls=[url])
    metadata = {
        "source_type": "url",
        "filename": url,
        "url": url,
    }
    return docs, metadata
