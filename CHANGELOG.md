# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-03-09

### Added
- Reranking support (optional) for improved retrieval quality
- Templates 1-3: Cohere Rerank (rerank-v3.5)
- Template 4: Voyage AI Rerank (rerank-2, uses existing API key)
- Over-fetch TOP_K × 3 candidates, rerank, keep top TOP_K
- Disabled by default (`RERANK_ENABLED=false`)

## [0.2.0] - 2026-03-09

### Added
- Hybrid search: vector + BM25 keyword with Reciprocal Rank Fusion (RRF)
- 3 search modes: `vector`, `keyword`, `hybrid` (default)
- `search_mode` parameter in query API and MCP tools
- Template 4: Claude API (Anthropic) + Voyage AI embeddings

### Changed
- MCP transport upgraded from SSE to Streamable HTTP
- MCP endpoint changed from `/sse` to `/mcp`
- `mcp[cli]` minimum version bumped to >=1.8.0
- `chromadb` version unpinned for compatibility

## [0.1.0] - 2026-03-08

### Added
- Initial release
- 3 RAG templates: No Framework, LangChain, LlamaIndex
- `ragforge.py` CLI for project scaffolding
- FastAPI server with REST endpoints (upload, ingest-url, query, list, delete)
- MCP server (SSE transport) for Claude Code integration
- Docker Compose support with health checks
- CORS middleware with configurable origins
- URL validation (SSRF protection)
- File size limits for uploads
- Non-root Docker user
- CLAUDE.md for each template
- GitHub CI/CD workflow
- Issue templates and PR template
- CONTRIBUTING.md and SECURITY.md
