#!/usr/bin/env python3
"""ragforge - Create RAG projects from templates."""

import argparse
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"

TEMPLATES = {
    "1": {
        "dir": "rag-01-no-framework",
        "name": "No Framework",
        "desc": "เขียนเองทั้งหมดจาก openai + chromadb + fastapi (ควบคุมได้สูงสุด)",
    },
    "2": {
        "dir": "rag-02-langchain",
        "name": "LangChain",
        "desc": "ใช้ LangChain framework (LCEL chain, loaders, text splitters)",
    },
    "3": {
        "dir": "rag-03-llamaindex",
        "name": "LlamaIndex",
        "desc": "ใช้ LlamaIndex framework (query engine, readers, index)",
    },
}


def print_banner():
    print(
        r"""
  ____             _____
 |  _ \ __ _  __ _|  ___|__  _ __ __ _  ___
 | |_) / _` |/ _` | |_ / _ \| '__/ _` |/ _ \
 |  _ < (_| | (_| |  _| (_) | | | (_| |  __/
 |_| \_\__,_|\__, |_|  \___/|_|  \__, |\___|
             |___/                |___/
    """
    )


def cmd_list(args):
    """List available templates."""
    print_banner()
    print("Available templates:\n")
    for key, t in TEMPLATES.items():
        print(f"  [{key}] {t['name']}")
        print(f"      {t['desc']}\n")
    print("Usage: ragforge new <project-name> -t <number>")


def pick_template():
    """Interactive template selection."""
    print("Available templates:\n")
    for key, t in TEMPLATES.items():
        print(f"  [{key}] {t['name']}")
        print(f"      {t['desc']}\n")

    while True:
        choice = input("Select template [1/2/3]: ").strip()
        if choice in TEMPLATES:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")


def create_env_file(dest: Path):
    """Create .env from .env.example, optionally filling in API key."""
    example = dest / ".env.example"
    env_file = dest / ".env"

    if not example.exists():
        return

    content = example.read_text()

    try:
        api_key = input("\nOpenAI API Key (Enter to skip): ").strip()
        if api_key:
            content = content.replace("sk-...", api_key)
    except EOFError:
        pass

    env_file.write_text(content)
    print(f"  Created .env")


def cmd_new(args):
    """Create a new project from template."""
    print_banner()

    project_name = args.name
    projects_dir = SCRIPT_DIR / "projects"
    projects_dir.mkdir(exist_ok=True)
    dest = projects_dir / project_name

    if dest.exists():
        print(f"Error: '{project_name}' already exists.")
        sys.exit(1)

    # Pick template
    if args.template:
        choice = args.template
        if choice not in TEMPLATES:
            print(f"Error: Invalid template '{choice}'. Use 1, 2, or 3.")
            sys.exit(1)
    else:
        choice = pick_template()

    template = TEMPLATES[choice]
    src = TEMPLATES_DIR / template["dir"]

    if not src.exists():
        print(f"Error: Template not found at {src}")
        sys.exit(1)

    print(f"\nCreating project '{project_name}' with [{template['name']}]...\n")

    # Copy template
    shutil.copytree(src, dest)
    print(f"  Copied template to projects/{project_name}/")

    # Create .env
    create_env_file(dest)

    # Summary
    file_count = sum(1 for _ in dest.rglob("*") if _.is_file())
    print(f"  Total files: {file_count}")

    print(f"""
Done! Next steps:

  cd projects/{project_name}

  # Run with Docker (recommended):
  docker-compose up --build

  # Or run locally:
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000
  python mcp_server.py  # MCP server on port 8001

  # API docs at http://localhost:8000/docs

  # Connect MCP to Claude Code:
  claude mcp add ragforge --transport sse http://localhost:8001/sse
""")


def main():
    parser = argparse.ArgumentParser(
        prog="ragforge",
        description="Create RAG projects from templates",
    )
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="List available templates")

    # new
    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("name", help="Project name")
    new_parser.add_argument(
        "-t", "--template",
        choices=["1", "2", "3"],
        help="Template: 1=No Framework, 2=LangChain, 3=LlamaIndex",
    )

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "new":
        cmd_new(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
