import os

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain_core.documents import Document


def load_pdf(file_path: str) -> tuple[list[Document], dict]:
    """Load PDF using LangChain PyMuPDFLoader."""
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    metadata = {
        "source_type": "pdf",
        "filename": os.path.basename(file_path),
    }
    return docs, metadata


def load_text(file_path: str) -> tuple[list[Document], dict]:
    """Load text/markdown using LangChain TextLoader."""
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    metadata = {
        "source_type": "text",
        "filename": os.path.basename(file_path),
    }
    return docs, metadata


def load_url(url: str) -> tuple[list[Document], dict]:
    """Load web page using LangChain WebBaseLoader."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    title = docs[0].metadata.get("title", url) if docs else url
    metadata = {
        "source_type": "url",
        "filename": title,
        "url": url,
    }
    return docs, metadata
