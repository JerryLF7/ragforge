from llama_index.core.prompts import PromptTemplate

from config import settings
from services.index import get_index

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based on the provided context.\n"
    "Use ONLY the context below to answer. If the context doesn't contain enough information, say so.\n"
    "Do not make up information.\n\n"
    "Context:\n{context_str}\n\n"
    "Question: {query_str}\n"
    "Answer: "
)

_qa_template = PromptTemplate(SYSTEM_PROMPT)


def ask(question: str, top_k: int | None = None) -> dict:
    """Run the full RAG pipeline using LlamaIndex query engine."""
    k = top_k or settings.top_k

    index = get_index()
    query_engine = index.as_query_engine(
        similarity_top_k=k,
        text_qa_template=_qa_template,
    )

    response = query_engine.query(question)

    # Extract sources from response
    sources = []
    for node in response.source_nodes:
        sources.append(
            {
                "id": node.node_id,
                "chunk_text": node.text,
                "score": node.score,
                "metadata": node.metadata,
            }
        )

    if not sources:
        return {
            "answer": "No relevant documents found. Please upload some documents first.",
            "sources": [],
        }

    return {
        "answer": str(response),
        "sources": sources,
    }
