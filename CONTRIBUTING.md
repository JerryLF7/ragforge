# Contributing to RagForge

Thank you for your interest in contributing! RagForge is an open-source project and we welcome contributions from developers worldwide.

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists in [GitHub Issues](https://github.com/monthop-gmail/ragforge/issues)
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Template number (1, 2, or 3) and environment details

### Suggesting Features

Open a [GitHub Issue](https://github.com/monthop-gmail/ragforge/issues) with the `enhancement` label. Describe:
- What problem it solves
- Proposed solution
- Which template(s) it affects

### Submitting Code

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test** your changes with at least one template
5. **Commit**: `git commit -m "Add: your feature description"`
6. **Push**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**

## Development Guidelines

### Code Style

- Python code follows PEP 8
- Use type hints where practical
- Keep functions focused and small
- Prefer simple, readable code over clever abstractions

### Adding a New Template

1. Create a new directory: `templates/rag-XX-your-template/`
2. Include all required files:
   - `main.py`, `config.py`, `models.py`
   - `routers/documents.py`, `routers/query.py`
   - `services/` (your RAG implementation)
   - `mcp_server.py` (copy from existing template)
   - `requirements.txt`, `Dockerfile`, `docker-compose.yml`
   - `.env.example`, `.gitignore`
   - `CLAUDE.md`
3. Ensure the API endpoints match the existing templates
4. Update `ragforge.py` to include your template
5. Update `README.md` with your template info

### API Compatibility

All templates **must** expose the same API endpoints:
- `POST /upload`
- `POST /ingest-url`
- `POST /query`
- `GET /documents`
- `DELETE /documents/{id}`
- `GET /health`

This ensures templates are interchangeable.

### Testing Your Changes

```bash
# Create a project from your modified template
python3 ragforge.py new test-project -t <number>
cd projects/test-project

# Test with Docker
docker compose up --build

# Verify all endpoints work
curl http://localhost:8000/health
curl http://localhost:8000/documents
curl http://localhost:8001/sse  # MCP server
```

## Commit Messages

Use clear, descriptive commit messages:

- `Add: new Qdrant vector store template`
- `Fix: PDF upload fails with large files`
- `Update: improve chunking performance`
- `Docs: add API usage examples`

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on the technical merits of contributions

## Questions?

Open an issue or start a discussion on GitHub. We're happy to help!
