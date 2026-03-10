import chromadb
from llama_index.core import Settings as LlamaSettings
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import settings

# Configure LlamaIndex global settings
LlamaSettings.llm = OpenAI(
    model=settings.openai_chat_model,
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
    temperature=0.2,
)
LlamaSettings.embed_model = OpenAIEmbedding(
    model_name=settings.openai_embedding_model,
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
)
LlamaSettings.node_parser = SentenceSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
)

# ChromaDB setup
_chroma_client = chromadb.PersistentClient(path=settings.chroma_path)
_chroma_collection = _chroma_client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"},
)
_vector_store = ChromaVectorStore(chroma_collection=_chroma_collection)
_storage_context = StorageContext.from_defaults(vector_store=_vector_store)


def get_index() -> VectorStoreIndex:
    """Get or create the VectorStoreIndex from ChromaDB."""
    return VectorStoreIndex.from_vector_store(
        vector_store=_vector_store,
    )


def get_storage_context() -> StorageContext:
    return _storage_context


def get_chroma_collection():
    return _chroma_collection
