import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings
from models import DeleteResponse, DocumentInfo, IngestResponse
from services import loaders, vector_store

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
)


@router.post("/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile):
    """Upload and ingest a document (PDF, TXT, MD)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}",
        )

    doc_id = str(uuid.uuid4())
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, f"{doc_id}_{file.filename}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        # Load using LangChain loaders
        if ext == ".pdf":
            docs, metadata = loaders.load_pdf(file_path)
        else:
            docs, metadata = loaders.load_text(file_path)

        # Split using LangChain text splitter
        chunks = _splitter.split_documents(docs)

        if not chunks:
            raise HTTPException(status_code=400, detail="Document contains no text")

        # Add to vector store (embedding handled by LangChain)
        chunk_count = vector_store.add_document(
            doc_id=doc_id,
            chunks=chunks,
            metadata=metadata,
        )

        return IngestResponse(
            document_id=doc_id,
            filename=file.filename,
            chunk_count=chunk_count,
            message="Document ingested successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/documents", response_model=list[DocumentInfo])
def list_documents():
    """List all ingested documents."""
    docs = vector_store.list_documents()
    return [DocumentInfo(**d) for d in docs]


@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
def delete_document(doc_id: str):
    """Delete a document and all its chunks."""
    deleted = vector_store.delete_document(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return DeleteResponse(message=f"Document {doc_id} deleted successfully")
