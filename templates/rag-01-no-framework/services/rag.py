from openai import OpenAI

from config import settings
from services.embeddings import embed_query
from services.vector_store import query as vector_query

_client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
Use ONLY the context below to answer. If the context doesn't contain enough information, say so.
Do not make up information."""


def ask(question: str, top_k: int | None = None) -> dict:
    """Run the full RAG pipeline: embed -> retrieve -> generate."""
    k = top_k or settings.top_k

    # 1. Embed the question
    query_embedding = embed_query(question)

    # 2. Retrieve relevant chunks
    results = vector_query(query_embedding, k)

    if not results:
        return {
            "answer": "No relevant documents found. Please upload some documents first.",
            "sources": [],
        }

    # 3. Build context
    context_parts = []
    for i, r in enumerate(results, 1):
        filename = r["metadata"].get("filename", "unknown")
        context_parts.append(f"[Source {i}] ({filename}):\n{r['chunk_text']}")
    context = "\n\n".join(context_parts)

    # 4. Call chat completion
    response = _client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": results,
    }
