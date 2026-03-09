import logging

import cohere

from config import settings

logger = logging.getLogger(__name__)

_client: cohere.Client | None = None


def _get_client() -> cohere.Client:
    global _client
    if _client is None:
        _client = cohere.Client(api_key=settings.cohere_api_key)
    return _client


def rerank(query: str, results: list[dict], top_k: int) -> list[dict]:
    """Rerank results using Cohere Rerank API."""
    if not results:
        return results

    client = _get_client()
    documents = [r["chunk_text"] for r in results]

    response = client.rerank(
        query=query,
        documents=documents,
        model=settings.cohere_rerank_model,
        top_n=top_k,
    )

    reranked = []
    for item in response.results:
        result = results[item.index].copy()
        result["score"] = item.relevance_score
        reranked.append(result)

    logger.info("Reranked %d -> %d results", len(results), len(reranked))
    return reranked
