from services.index import get_chroma_collection


def list_documents() -> list[dict]:
    """List all unique documents in the store."""
    collection = get_chroma_collection()
    all_data = collection.get()
    if not all_data["ids"]:
        return []

    docs = {}
    for meta in all_data["metadatas"]:
        doc_id = meta.get("document_id", "unknown")
        if doc_id not in docs:
            docs[doc_id] = {
                "id": doc_id,
                "filename": meta.get("filename", "unknown"),
                "source_type": meta.get("source_type", "unknown"),
                "chunk_count": 0,
            }
        docs[doc_id]["chunk_count"] += 1

    return list(docs.values())


def delete_document(doc_id: str) -> bool:
    """Delete all chunks for a document."""
    collection = get_chroma_collection()
    results = collection.get(where={"document_id": doc_id})
    if not results["ids"]:
        return False
    collection.delete(ids=results["ids"])
    return True
