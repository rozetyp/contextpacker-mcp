# ContextPacker MCP Server

Give any MCP-compatible AI agent instant access to **any GitHub repository** — without pasting files manually.

```
"How does authentication work in expressjs/express?"
→ agent fetches exactly the relevant files, packed within your token budget
```

Works with Claude Desktop, Cursor, Windsurf, VS Code (GitHub Copilot), and any other MCP client.

> **Hosted API: [contextpacker.com](https://contextpacker.com)** — 100 free requests, no card required.
> This is early software. If something doesn't work as expected, please [open an issue](https://github.com/rozetyp/contextpacker-mcp/issues) — feedback is very welcome.

---

## Tools

| Tool | Description |
|------|-------------|
| `get_context(repo_url, query, max_tokens?)` | Selects and packs the most relevant files for a question |
| `get_skeleton(repo_url)` | Returns the full annotated file tree (repo map) without file contents |

Both tools support public repos out of the box. For private repos, add a GitHub PAT (see below).

---

## Quick start

> **Note:** The package is not yet on PyPI. Use Option B (run from source) for now.
> PyPI / `uvx` support is coming soon.

### Option A — `uvx` *(coming soon)*

```bash
uvx contextpacker-mcp
```

### Option B — run from source *(works now)*

```bash
git clone https://github.com/rozetyp/contextpacker-mcp
cd contextpacker-mcp
python -m venv .venv && source .venv/bin/activate
pip install -e .
python server.py  # verify it starts
```

Then point your MCP client at the `server.py` file (see [Configure your MCP client](#configure-your-mcp-client)).

---

## Get an API key

Get a free key (100 requests, no card required) at **[contextpacker.com](https://contextpacker.com)**.

For running without an API key, see [Self-hosting](#self-hosting).

---

## Configure your MCP client

First clone the repo and note the full path to `server.py` (e.g. `/Users/you/contextpacker-mcp/server.py`).
Replace that path and `cp_live_your_key_here` with your actual values in the snippets below.

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "contextpacker": {
      "command": "python3",
      "args": ["/path/to/contextpacker-mcp/server.py"],
      "env": {
        "CONTEXTPACKER_API_KEY": "cp_live_your_key_here"
      }
    }
  }
}
```

### Cursor

Create or edit `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "contextpacker": {
      "command": "python3",
      "args": ["/path/to/contextpacker-mcp/server.py"],
      "env": {
        "CONTEXTPACKER_API_KEY": "cp_live_your_key_here"
      }
    }
  }
}
```

### Windsurf

Edit `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "contextpacker": {
      "command": "python3",
      "args": ["/path/to/contextpacker-mcp/server.py"],
      "env": {
        "CONTEXTPACKER_API_KEY": "cp_live_your_key_here"
      }
    }
  }
}
```

### VS Code (GitHub Copilot)

Add to `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "contextpacker": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/contextpacker-mcp/server.py"],
      "env": {
        "CONTEXTPACKER_API_KEY": "cp_live_your_key_here"
      }
    }
  }
}
```

---

## Private repositories

Add your GitHub Personal Access Token (needs `repo` scope) to the `env` block:

```json
"env": {
  "CONTEXTPACKER_API_KEY": "cp_live_your_key_here",
  "GITHUB_PAT": "ghp_your_token_here"
}
```

---

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CONTEXTPACKER_API_KEY` | Yes (hosted) | — | API key from contextpacker.com |
| `CONTEXTPACKER_API_URL` | No | `https://contextpacker.com` | Override for self-hosted instances |
| `GITHUB_PAT` | No | — | GitHub PAT for private repo access (`repo` scope) |

---

## Self-hosting

Run the full ContextPacker server locally — no API key needed:

```bash
git clone https://github.com/rozetyp/contextpacker
cd contextpacker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export LLM_API_KEY=your_gemini_or_openai_key
uvicorn context_packer.main:app --port 8000
```

Then in your MCP client config, omit `CONTEXTPACKER_API_KEY` and add:

```json
"env": {
  "CONTEXTPACKER_API_URL": "http://localhost:8000"
}
```

---

## How it works

```
get_context(repo_url, "how does routing work?")
    ↓
Shallow clone (depth=1) — or warm cache hit (~1s)
    ↓
Build file tree, extract AST symbols per file
    ↓
LLM ranks and selects the most relevant files
    ↓
Pack selected files into Markdown within your token budget
    ↓
Return context with per-file reason comments
```

First call for a repo: 3–10s (clone + index). Subsequent calls: ~1s.

---

## Development

```bash
git clone https://github.com/rozetyp/contextpacker-mcp
cd contextpacker-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Test with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python3 server.py
# Opens http://localhost:6274 — test tools directly in your browser
```

---

## Feedback

This is early software under active development. If you:
- Can't get it working → [open an issue](https://github.com/rozetyp/contextpacker-mcp/issues)
- Get bad context results for a repo → let us know with a minimal example
- Want to request a new MCP client config or feature → open an issue

A ⭐ on GitHub helps more developers find this.

---

## Contributing

Bug reports and pull requests are welcome. Please open an issue first for larger changes.

---

## License

MIT — see [LICENSE](LICENSE).
