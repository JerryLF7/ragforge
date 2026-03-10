from openai import OpenAI

from config import settings

_client = OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns list of embedding vectors."""
    response = _client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]
