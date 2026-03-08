import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile
from llama_index.core import VectorStoreIndex

from config import settings
from models import DeleteResponse, DocumentInfo, IngestResponse
from services import loaders, vector_store
from services.index import get_storage_context

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


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
        # Load documents
        if ext == ".pdf":
            docs, metadata = loaders.load_pdf(file_path)
        else:
            docs, metadata = loaders.load_text(file_path)

        if not docs:
            raise HTTPException(status_code=400, detail="Document contains no text")

        # Add document_id to metadata for tracking
        for doc in docs:
            doc.metadata.update(metadata)
            doc.metadata["document_id"] = doc_id

        # Index documents (LlamaIndex handles chunking + embedding + storing)
        storage_context = get_storage_context()
        VectorStoreIndex.from_documents(
            documents=docs,
            storage_context=storage_context,
        )

        # Count chunks stored
        collection = vector_store.get_chroma_collection() if hasattr(vector_store, 'get_chroma_collection') else None
        chunk_count = len(docs)  # approximate

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
