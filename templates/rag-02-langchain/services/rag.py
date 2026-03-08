from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import settings
from services.vector_store import query as vector_query

_llm = ChatOpenAI(
    model=settings.openai_chat_model,
    openai_api_key=settings.openai_api_key,
    temperature=0.2,
)

_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that answers questions based on the provided context.\n"
            "Use ONLY the context below to answer. If the context doesn't contain enough information, say so.\n"
            "Do not make up information.",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)

_chain = _prompt | _llm | StrOutputParser()


def ask(question: str, top_k: int | None = None) -> dict:
    """Run the full RAG pipeline using LangChain LCEL."""
    k = top_k or settings.top_k

    # 1. Retrieve relevant chunks (embedding is handled by vector_store)
    results = vector_query(question, k)

    if not results:
        return {
            "answer": "No relevant documents found. Please upload some documents first.",
            "sources": [],
        }

    # 2. Build context
    context_parts = []
    for i, r in enumerate(results, 1):
        filename = r["metadata"].get("filename", "unknown")
        context_parts.append(f"[Source {i}] ({filename}):\n{r['chunk_text']}")
    context = "\n\n".join(context_parts)

    # 3. Run chain
    answer = _chain.invoke({"context": context, "question": question})

    return {
        "answer": answer,
        "sources": results,
    }
