# ContextPacker MCP Server

Give any MCP-compatible AI agent instant access to **any GitHub repository** — without pasting files manually.

```
"How does authentication work in expressjs/express?"
→ agent fetches exactly the relevant files, packed within your token budget
```

Works with Claude Desktop, Cursor, Windsurf, VS Code (GitHub Copilot), and any other MCP client.

---

## Tools

| Tool | Description |
|------|-------------|
| `get_context(repo_url, query, max_tokens?)` | Selects and packs the most relevant files for a question |
| `get_skeleton(repo_url)` | Returns the full annotated file tree (repo map) without file contents |

Both tools support public repos out of the box. For private repos, add a GitHub PAT (see below).

---

## Quick start

### Option A — `uvx` (no install, recommended)

If you have [`uv`](https://docs.astral.sh/uv/) installed:

```bash
uvx contextpacker-mcp
```

`uvx` downloads and runs the package in an isolated environment automatically. No pip, no virtualenv.

### Option B — `pip install`

```bash
pip install contextpacker-mcp
contextpacker-mcp   # verify it starts
```

### Option C — run from source

```bash
git clone https://github.com/rozetyp/contextpacker-mcp
cd contextpacker-mcp
pip install .
python server.py
```

---

## Get an API key

Get a free key (100 requests, no card required) at **[contextpacker.com](https://contextpacker.com)**.

For running without an API key, see [Self-hosting](#self-hosting).

---

## Configure your MCP client

Replace `cp_live_your_key_here` with your actual API key in the snippets below.

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "contextpacker": {
      "command": "uvx",
      "args": ["contextpacker-mcp"],
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
      "command": "uvx",
      "args": ["contextpacker-mcp"],
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
      "command": "uvx",
      "args": ["contextpacker-mcp"],
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
      "command": "uvx",
      "args": ["contextpacker-mcp"],
      "env": {
        "CONTEXTPACKER_API_KEY": "cp_live_your_key_here"
      }
    }
  }
}
```

> **Not using `uvx`?** Replace `"command": "uvx", "args": ["contextpacker-mcp"]` with
> `"command": "python", "args": ["/absolute/path/to/server.py"]`.

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
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Test with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python server.py
# Opens http://localhost:6274 — test tools directly in your browser
```

---

## Contributing

Bug reports and pull requests are welcome. Please open an issue first for larger changes.

---

## License

MIT — see [LICENSE](LICENSE).
