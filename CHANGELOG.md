# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-03-09

### Added
- Hybrid search: vector + BM25 keyword with Reciprocal Rank Fusion (RRF)
- 3 search modes: `vector`, `keyword`, `hybrid` (default)
- `search_mode` parameter in query API and MCP tools

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
