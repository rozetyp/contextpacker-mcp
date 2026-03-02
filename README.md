# ContextPacker MCP Server

Give any MCP-compatible AI agent (Claude Desktop, Cursor, Windsurf, etc.) instant access to any GitHub repository.

**One line, any repo, any question:**
```
get_context("https://github.com/pallets/flask", "How does routing work?")
```

Returns the most relevant files packed into a single Markdown block — ready to use as context.

---

## Tools

| Tool | What it does |
|------|-------------|
| `get_context(repo_url, query, max_tokens?)` | Select + pack the most relevant files for a question |
| `get_skeleton(repo_url)` | Return the full annotated file tree (repo map) |

---

## Setup

### 1. Install

```bash
pip install mcp httpx
```

### 2. Get an API key (or self-host)

**Option A — Hosted (recommended):** Get a free key at [contextpacker.com](https://contextpacker.com). 100 free requests, no card required.

**Option B — Self-hosted:** Run the ContextPacker server locally and point the MCP server at it:
```bash
# In contextpacker repo:
uvicorn context_packer.main:app --port 8000

# Then set:
export CONTEXTPACKER_API_URL=http://localhost:8000
```

### 3. Configure your MCP client

**Claude Desktop** — add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "contextpacker": {
      "command": "python",
      "args": ["/path/to/contextpacker-mcp/server.py"],
      "env": {
        "CONTEXTPACKER_API_KEY": "cp_live_your_key_here"
      }
    }
  }
}
```

**Cursor** — add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "contextpacker": {
      "command": "python",
      "args": ["/path/to/contextpacker-mcp/server.py"],
      "env": {
        "CONTEXTPACKER_API_KEY": "cp_live_your_key_here"
      }
    }
  }
}
```

**Private repos** — add your GitHub PAT to the env block:
```json
"env": {
  "CONTEXTPACKER_API_KEY": "cp_live_your_key_here",
  "GITHUB_PAT": "ghp_your_pat_here"
}
```

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CONTEXTPACKER_API_KEY` | Yes (hosted) | API key from contextpacker.com |
| `CONTEXTPACKER_API_URL` | No | Override API URL for self-hosting (default: `https://contextpacker.com`) |
| `GITHUB_PAT` | No | GitHub PAT for private repo access |

---

## Examples

Once configured, just ask your agent naturally:

> "How does authentication work in this repo?"
> *→ agent calls `get_context("https://github.com/...", "authentication")`*

> "Give me a map of the codebase before I start"
> *→ agent calls `get_skeleton("https://github.com/...")`*

> "How does rate limiting work in our internal API?"
> *→ agent calls `get_context` with your private repo URL + GITHUB_PAT*

---

## How it works

```
get_context(repo_url, query)
    ↓
Clone repo (shallow, depth=1) or use warm cache
    ↓
Build annotated file tree with AST-extracted symbols
    ↓
LLM selects most relevant files for your query
    ↓
Pack files into Markdown within your token budget
    ↓
Return context with per-file reason comments
```

First call for a repo takes 3–8s (clone + index). Subsequent calls are cached: ~1s.

---

## License

MIT
