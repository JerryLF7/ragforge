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
- **MCP**: FastMCP SSE server (port 8001)

## Project Structure
```
├── main.py                 # FastAPI entrypoint
├── config.py               # Settings from .env (pydantic-settings)
├── models.py               # Pydantic request/response schemas
├── mcp_server.py           # MCP SSE server wrapping RAG API
├── routers/
│   ├── documents.py        # POST /upload, GET /documents, DELETE /documents/{id}
│   └── query.py            # POST /query, POST /ingest-url
├── services/
│   ├── chunker.py          # Recursive character text splitter (custom)
│   ├── embeddings.py       # OpenAI embedding wrapper
│   ├── vector_store.py     # ChromaDB wrapper (add, query, list, delete)
│   ├── loaders.py          # PDF, text, URL loaders
│   └── rag.py              # Retrieve + Generate pipeline
├── docker-compose.yml      # rag-server + mcp-server
└── .env                    # OPENAI_API_KEY and settings
```

## API Endpoints
- `POST /upload` — Upload PDF/TXT/MD file
- `POST /ingest-url` — Ingest web page by URL
- `POST /query` — Ask a question (RAG)
- `GET /documents` — List all documents
- `DELETE /documents/{id}` — Delete a document
- `GET /health` — Health check

## MCP Tools (port 8001)
- `rag_query` — Ask a question
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

## Running
```bash
# Docker (recommended)
docker compose up --build

# Local
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
python mcp_server.py  # separate terminal

# MCP for Claude Code
claude mcp add ragforge --transport sse http://localhost:8001/sse
```

## Key Design Decisions
- Chunker uses recursive splitting with separators: `\n\n` → `\n` → `. ` → ` ` → `""`
- Embeddings are batched in groups of 100 chunks per API call
- ChromaDB uses `upsert` to prevent duplicates on re-upload
- Uploaded files are cleaned up after ingestion (not stored permanently)
- MCP server is a separate process that calls RAG API via HTTP internally
