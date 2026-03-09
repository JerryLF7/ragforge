# RAG Server - No Framework

## Overview
RAG (Retrieval-Augmented Generation) server built from scratch using OpenAI + ChromaDB + FastAPI. No LangChain/LlamaIndex — full control over every component.

## Tech Stack
- **API**: FastAPI (port 8000)
- **LLM**: OpenAI GPT (gpt-4o-mini default)
- **Embedding**: OpenAI text-embedding-3-small
- **Vector DB**: ChromaDB (PersistentClient, cosine distance)
- **PDF**: PyMuPDF (fitz)
- **Web scraping**: requests + BeautifulSoup4
- **MCP**: FastMCP Streamable HTTP server (port 8001)

## Project Structure
```
├── main.py                 # FastAPI entrypoint
├── config.py               # Settings from .env (pydantic-settings)
├── models.py               # Pydantic request/response schemas
├── mcp_server.py           # MCP Streamable HTTP server wrapping RAG API
├── routers/
│   ├── documents.py        # POST /upload, GET /documents, DELETE /documents/{id}
│   └── query.py            # POST /query, POST /ingest-url
├── services/
│   ├── chunker.py          # Recursive character text splitter (custom)
│   ├── embeddings.py       # OpenAI embedding wrapper
│   ├── vector_store.py     # ChromaDB wrapper (add, query, list, delete)
│   ├── keyword_search.py   # BM25 keyword search (rank-bm25)
│   ├── hybrid_search.py    # Reciprocal Rank Fusion (RRF) merger
│   ├── reranker.py         # Cohere Rerank (optional)
│   ├── loaders.py          # PDF, text, URL loaders
│   └── rag.py              # Retrieve + Generate pipeline (vector/keyword/hybrid)
├── docker-compose.yml      # rag-server + mcp-server
└── .env                    # OPENAI_API_KEY and settings
```

## API Endpoints
- `POST /upload` — Upload PDF/TXT/MD file
- `POST /ingest-url` — Ingest web page by URL
- `POST /query` — Ask a question (RAG) with search_mode: vector/keyword/hybrid
- `GET /documents` — List all documents
- `DELETE /documents/{id}` — Delete a document
- `GET /health` — Health check

## MCP Tools (port 8001)
- `rag_query` — Ask a question (supports search_mode: vector/keyword/hybrid)
- `rag_upload_text` — Upload text content
- `rag_ingest_url` — Ingest from URL
- `rag_list_documents` — List documents
- `rag_delete_document` — Delete document

## Configuration (.env)
- `OPENAI_API_KEY` — Required
- `OPENAI_CHAT_MODEL` — Default: gpt-4o-mini
- `OPENAI_EMBEDDING_MODEL` — Default: text-embedding-3-small
- `CHUNK_SIZE` — Default: 1000
- `CHUNK_OVERLAP` — Default: 200
- `TOP_K` — Default: 5
- `RRF_K` — RRF constant for hybrid search. Default: 60
- `RERANK_ENABLED` — Enable reranking. Default: false
- `COHERE_API_KEY` — Cohere API key (required if reranking enabled)
- `COHERE_RERANK_MODEL` — Default: rerank-v3.5

## Running
```bash
# Docker (recommended)
docker compose up --build

# Local
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
python mcp_server.py  # separate terminal

# MCP for Claude Code
claude mcp add ragforge --transport http http://localhost:8001/mcp
```

## Hybrid Search
- **Vector search**: Cosine similarity via ChromaDB HNSW index (semantic matching)
- **Keyword search**: BM25 via rank-bm25 library (exact term matching)
- **Hybrid search** (default): Runs both, merges results using Reciprocal Rank Fusion (RRF)
- BM25 index is built on startup and rebuilt after each ingest/delete
- Query API accepts `search_mode`: `"vector"`, `"keyword"`, or `"hybrid"`

## Reranking (Optional)
- Disabled by default (`RERANK_ENABLED=false`)
- Uses Cohere Rerank v3.5 to re-score retrieved chunks by semantic relevance
- When enabled: retrieves TOP_K * 3 candidates, reranks, keeps top TOP_K
- Requires `COHERE_API_KEY` in `.env`

## Key Design Decisions
- Chunker uses recursive splitting with separators: `\n\n` → `\n` → `. ` → ` ` → `""`
- Embeddings are batched in groups of 100 chunks per API call
- ChromaDB uses `upsert` to prevent duplicates on re-upload
- Uploaded files are cleaned up after ingestion (not stored permanently)
- MCP server uses Streamable HTTP transport (replaces deprecated SSE)
