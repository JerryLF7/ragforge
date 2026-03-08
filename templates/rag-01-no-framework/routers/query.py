import uuid

from fastapi import APIRouter, HTTPException

from config import settings
from models import IngestResponse, IngestURLRequest, QueryRequest, QueryResponse, SourceInfo
from services import chunker, embeddings, loaders, rag, vector_store

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_documents(req: QueryRequest):
    """Ask a question using RAG."""
    try:
        result = rag.ask(question=req.question, top_k=req.top_k)
        return QueryResponse(
            answer=result["answer"],
            sources=[SourceInfo(**s) for s in result["sources"]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest-url", response_model=IngestResponse)
def ingest_url(req: IngestURLRequest):
    """Ingest content from a URL."""
    try:
        text, metadata = loaders.load_url(req.url)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found at URL")

        doc_id = str(uuid.uuid4())

        # Chunk
        chunks = chunker.split_text(
            text,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        # Embed
        all_embeddings = []
        for i in range(0, len(chunks), 100):
            batch = chunks[i : i + 100]
            all_embeddings.extend(embeddings.embed_texts(batch))

        # Store
        chunk_count = vector_store.add_document(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=all_embeddings,
            metadata=metadata,
        )

        return IngestResponse(
            document_id=doc_id,
            filename=metadata.get("filename", req.url),
            chunk_count=chunk_count,
            message="URL content ingested successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
