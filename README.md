# LLM-Orchestrated Dev Environment Automation

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![Llama 3.2](https://img.shields.io/badge/LLM-Llama%203.2-orange)

An intelligent CLI tool that generates complete, production-ready, and containerized development environments from natural language prompts using Agentic Self-Healing Infrastructure-as-Code.

## Why this exists

Instead of manually writing `docker-compose.yml`, `Dockerfile`, and `.devcontainer/devcontainer.json` files or prompting an LLM file-by-file, this tool:
1. **Plans the architecture** based on your prompt.
2. **Generates the entire file tree** atomically using structured JSON extraction.
3. **Validates it via dry-run** against your local Docker daemon (`docker-compose config`).
4. **Self-heals** by feeding Docker syntax errors back to the LLM for correction.

## Stack
- Python 3.11+
- Click & Rich for UI
- Pydantic & Instructor for structured extraction
- LiteLLM + Ollama (Llama 3.2 locally)

## How to use

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .

# Run the tool
dev-env generate "A Node.js backend with a Postgres database and Redis cache, including VS Code devcontainer setup"
```
