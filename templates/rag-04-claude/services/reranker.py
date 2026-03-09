import logging

import voyageai

from config import settings

logger = logging.getLogger(__name__)

_client: voyageai.Client | None = None


def _get_client() -> voyageai.Client:
    global _client
    if _client is None:
        _client = voyageai.Client(api_key=settings.voyage_api_key)
    return _client


def rerank(query: str, results: list[dict], top_k: int) -> list[dict]:
    """Rerank results using Voyage AI Rerank API."""
    if not results:
        return results

    client = _get_client()
    documents = [r["chunk_text"] for r in results]

    response = client.rerank(
        query=query,
        documents=documents,
        model=settings.voyage_rerank_model,
        top_k=top_k,
    )

    reranked = []
    for item in response.results:
        result = results[item.index].copy()
        result["score"] = item.relevance_score
        reranked.append(result)

    logger.info("Reranked %d -> %d results", len(results), len(reranked))
    return reranked
