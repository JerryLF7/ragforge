# RagForge

**Create production-ready RAG servers in seconds.**

RagForge is a CLI tool that scaffolds complete RAG (Retrieval-Augmented Generation) projects from battle-tested templates. Choose your framework, run one command, and get a fully working RAG server with API endpoints and MCP integration.

```bash
python3 ragforge.py new my-knowledge-base -t 1
```

```
my-knowledge-base/
├── main.py              # FastAPI server
├── mcp_server.py        # MCP server (SSE)
├── services/            # RAG pipeline
├── docker-compose.yml   # One-command deployment
└── .env                 # Your config
```

## Templates

| # | Template | Framework | Best For |
|---|----------|-----------|----------|
| 1 | **No Framework** | openai + chromadb + fastapi | Full control, learning, customization |
| 2 | **LangChain** | langchain + langchain-openai | Ecosystem integration, rapid prototyping |
| 3 | **LlamaIndex** | llama-index + integrations | Minimal code, highest abstraction |

All templates share the **same API surface** — swap frameworks without changing your client code.

### Template Comparison

| Feature | No Framework | LangChain | LlamaIndex |
|---------|:------------:|:---------:|:----------:|
| Chunking | Custom recursive splitter | RecursiveCharacterTextSplitter | SentenceSplitter (auto) |
| Embedding | Direct OpenAI API | OpenAIEmbeddings | OpenAIEmbedding |
| Vector Store | Direct ChromaDB | langchain-chroma | ChromaVectorStore |
| Hybrid Search | BM25 + RRF | BM25 + RRF | BM25 + RRF |
| RAG Pipeline | Manual (embed→retrieve→prompt→chat) | LCEL chain | retriever + llm.complete() |
| Control Level | High | Medium | Low |
| Lines of Code | Most | Medium | Least |

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- OpenAI API key

### 1. Create a Project

```bash
# Clone this repo
git clone https://github.com/monthop-gmail/ragforge.git
cd ragforge

# Interactive mode
python3 ragforge.py new my-project

# Or specify template directly
python3 ragforge.py new my-project -t 1   # No Framework
python3 ragforge.py new my-project -t 2   # LangChain
python3 ragforge.py new my-project -t 3   # LlamaIndex
```

### 2. Configure

```bash
cd projects/my-project
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run

```bash
# Docker (recommended) — starts RAG server + MCP server
docker compose up --build

# Or run locally
pip install -r requirements.txt
uvicorn main:app --reload --port 8000      # RAG API
python mcp_server.py                        # MCP server (separate terminal)
```

### 4. Use

```bash
# API docs
open http://localhost:8000/docs

# Upload a document
curl -X POST http://localhost:8000/upload -F "file=@document.pdf"

# Ask a question (hybrid search by default)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'

# Use specific search mode
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "exact term lookup", "search_mode": "keyword"}'

# Connect to Claude Code via MCP
claude mcp add ragforge --transport sse http://localhost:8001/sse
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload` | Upload a document (PDF, TXT, MD) |
| `POST` | `/ingest-url` | Ingest content from a URL |
| `POST` | `/query` | Ask a question using RAG (supports `search_mode`: vector/keyword/hybrid) |
| `GET` | `/documents` | List all ingested documents |
| `DELETE` | `/documents/{id}` | Delete a document |
| `GET` | `/health` | Health check |

## MCP Integration

Every template includes an MCP (Model Context Protocol) server that exposes RAG functionality as tools for AI assistants like Claude.

**Available MCP Tools:**

| Tool | Description |
|------|-------------|
| `rag_query` | Ask a question (supports `search_mode`: vector/keyword/hybrid) |
| `rag_upload_text` | Upload text content |
| `rag_ingest_url` | Ingest content from a URL |
| `rag_list_documents` | List all documents |
| `rag_delete_document` | Delete a document by ID |

**Setup with Claude Code:**

```bash
claude mcp add ragforge --transport sse http://localhost:8001/sse
```

## Hybrid Search

All templates support **3 search modes** out of the box:

| Mode | How It Works | Best For |
|------|-------------|----------|
| `hybrid` (default) | Vector + BM25 keyword, merged with RRF | General use — best overall quality |
| `vector` | Cosine similarity via ChromaDB HNSW | Semantic/conceptual questions |
| `keyword` | BM25 term matching via rank-bm25 | Exact term lookup, names, codes |

**Reciprocal Rank Fusion (RRF)** combines results from both search methods by rank position, so no score normalization is needed. The BM25 index is built on startup and auto-rebuilt after every ingest/delete.

```bash
# Default hybrid search
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "how does authentication work?", "search_mode": "hybrid"}'
```

## Architecture

```
                    ┌─────────────────────┐
                    │   Claude Code / AI   │
                    └──────────┬──────────┘
                               │ MCP (SSE)
                    ┌──────────▼──────────┐
                    │   MCP Server :8001   │
                    └──────────┬──────────┘
                               │ HTTP
                    ┌──────────▼──────────┐
                    │  FastAPI RAG :8000   │
                    │  ┌────────────────┐  │
  Documents ───────►│  │   Loaders      │  │
  (PDF/TXT/URL)     │  │   Chunker      │  │
                    │  │   Embeddings   │  │
                    │  └───────┬────────┘  │
                    │  ┌───────▼────────┐  │
                    │  │   ChromaDB     │  │
                    │  │  (Vector DB)   │  │
                    │  └───────┬────────┘  │
                    │  ┌───────▼────────┐  │
  Question ────────►│  │  Hybrid Search │──► Vector + BM25
                    │  │  (RRF Fusion)  │  │
                    │  └───────┬────────┘  │
                    │  ┌───────▼────────┐  │
                    │  │  RAG Pipeline  │──►  Answer + Sources
                    │  │  (OpenAI LLM)  │  │
                    │  └────────────────┘  │
                    └─────────────────────┘
```

## Configuration

All templates use the same `.env` configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat model for generation |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `TOP_K` | `5` | Number of chunks to retrieve |
| `RRF_K` | `60` | RRF constant for hybrid search ranking |
| `CHROMA_PATH` | `./data/chroma` | ChromaDB storage path |

## Project Structure

```
ragforge/
├── ragforge.py              # CLI tool
├── templates/
│   ├── rag-01-no-framework/ # Template 1: Pure Python
│   ├── rag-02-langchain/    # Template 2: LangChain
│   └── rag-03-llamaindex/   # Template 3: LlamaIndex
└── projects/                # Your created projects
```

## Contributing

We welcome contributions from developers worldwide! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- **New Templates** — Add support for different LLMs (Claude, Gemini, Ollama), vector DBs (Pinecone, Qdrant, Weaviate), or frameworks
- **Features** — Multi-modal RAG, reranking, conversation memory
- **Improvements** — Better chunking strategies, error handling, testing, documentation
- **Bug Fixes** — Report issues or submit fixes
- **Translations** — Help translate documentation

### Development Setup

```bash
git clone https://github.com/monthop-gmail/ragforge.git
cd ragforge
# Pick a template and test your changes
python3 ragforge.py new test-project -t 1
cd projects/test-project
docker compose up --build
```

## Roadmap

- [ ] Support for Claude API (Anthropic)
- [ ] Support for Ollama (local LLM)
- [ ] Support for Gemini API
- [ ] Pinecone / Qdrant / Weaviate vector store templates
- [ ] Multi-modal RAG (images, tables)
- [x] Hybrid search (vector + BM25 keyword + RRF)
- [ ] Reranking (Cohere, cross-encoder)
- [ ] Conversation memory / chat history
- [ ] Authentication & API keys for endpoints
- [ ] Web UI for document management
- [ ] `pip install ragforge` (PyPI package)

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Built with** Python, FastAPI, OpenAI, ChromaDB, and MCP.

If RagForge helps you, give it a star on GitHub!
