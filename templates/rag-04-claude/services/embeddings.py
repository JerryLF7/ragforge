import voyageai

from config import settings

_client = voyageai.Client(api_key=settings.voyage_api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using Voyage AI. Returns list of embedding vectors."""
    result = _client.embed(texts, model=settings.voyage_embedding_model)
    return result.embeddings


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    result = _client.embed([text], model=settings.voyage_embedding_model, input_type="query")
    return result.embeddings[0]
