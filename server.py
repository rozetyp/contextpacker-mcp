"""
ContextPacker MCP Server

Exposes two tools to any MCP-compatible AI agent (Claude, Cursor, Windsurf, etc.):

  - get_context  : Select and pack the most relevant files from a repo for a question
  - get_skeleton : Return the full annotated file tree (repo map) without selecting files

Supports two modes:
  - Hosted  : Set CONTEXTPACKER_API_KEY → calls contextpacker.com (no setup, private repos supported)
  - Self-hosted : Set CONTEXTPACKER_API_URL to your own instance (e.g. http://localhost:8000)

Usage with Claude Desktop, Cursor, or any MCP client — see README.md.
"""

import os
import sys
import httpx
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: 'mcp' package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# =============================================================================
# Configuration
# =============================================================================

API_KEY = os.environ.get("CONTEXTPACKER_API_KEY", "")
API_URL = os.environ.get("CONTEXTPACKER_API_URL", "https://contextpacker.com").rstrip("/")
GITHUB_PAT = os.environ.get("GITHUB_PAT", "")

# Timeout for API calls (repos can take a few seconds to clone on first request)
HTTP_TIMEOUT = 60.0

# =============================================================================
# MCP server
# =============================================================================

mcp = FastMCP("ContextPacker")


def _headers() -> dict:
    """Build request headers. Works with or without an API key."""
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["X-API-Key"] = API_KEY
    return h


def _vcs_block() -> Optional[dict]:
    """Add GitHub PAT block if set, for private repo access."""
    if GITHUB_PAT:
        return {"provider": "github", "token": GITHUB_PAT}
    return None


# =============================================================================
# Tool: get_context
# =============================================================================

@mcp.tool()
def get_context(
    repo_url: str,
    query: str,
    max_tokens: int = 8000,
) -> str:
    """
    Retrieve the most relevant source files from a GitHub repository, packed into
    a single Markdown block optimised for your token budget.

    How it works:
      1. Clones the repo (shallow, depth=1) or uses a warm cache
      2. Builds an annotated file tree with AST-extracted symbols
      3. Uses an LLM to select the most relevant files for your query
      4. Packs selected files into Markdown, truncating to fit max_tokens

    Args:
        repo_url:   GitHub repository URL (e.g. https://github.com/pallets/flask)
        query:      Natural language question about the codebase
        max_tokens: Token budget for the returned context (default 8000, max 100000)

    Returns:
        Markdown string with selected files and a <!-- reason="..." --> comment
        per file explaining why it was included. Paste directly into your prompt.

    Examples:
        get_context("https://github.com/pallets/flask", "How does routing work?")
        get_context("https://github.com/expressjs/express", "Where is middleware applied?", 12000)
    """
    payload: dict = {
        "repo_url": repo_url,
        "query": query,
        "max_tokens": max_tokens,
    }

    vcs = _vcs_block()
    if vcs:
        payload["vcs"] = vcs

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.post(f"{API_URL}/v1/packs", headers=_headers(), json=payload)

        if resp.status_code == 401:
            return (
                "Error: Unauthorized. Set CONTEXTPACKER_API_KEY environment variable.\n"
                "Get a free key at https://contextpacker.com"
            )
        if resp.status_code == 404:
            return f"Error: Repository not found or is private. If private, set GITHUB_PAT.\nURL: {repo_url}"
        if resp.status_code == 422:
            detail = resp.json().get("detail", resp.text)
            return f"Error processing repository: {detail}"
        if not resp.is_success:
            return f"API error {resp.status_code}: {resp.text[:500]}"

        data = resp.json()
        markdown = data.get("markdown", "")
        stats = data.get("stats", {})

        summary = (
            f"<!-- contextpacker: {stats.get('files_selected', '?')} files · "
            f"{stats.get('tokens_packed', '?')} tokens packed · "
            f"{stats.get('tokens_raw_repo', '?')} raw repo tokens · "
            f"cache_hit={stats.get('cache_hit', False)} -->\n\n"
        )
        return summary + markdown

    except httpx.TimeoutException:
        return (
            "Error: Request timed out. The repository may be large or the server is busy.\n"
            "Try again — subsequent requests use a warm cache and are much faster."
        )
    except httpx.RequestError as e:
        return f"Error: Could not reach ContextPacker API at {API_URL}.\nDetails: {e}"


# =============================================================================
# Tool: get_skeleton
# =============================================================================

@mcp.tool()
def get_skeleton(repo_url: str) -> str:
    """
    Return an annotated file tree (semantic skeleton) for a GitHub repository.

    The skeleton shows every file with inline symbol hints extracted via AST:
      src/auth/login.py  [login_user, verify_token, hash_password]
      src/models/user.py  # User model for authentication

    Use this to orient yourself in an unfamiliar codebase before asking more
    specific questions with get_context.

    Args:
        repo_url: GitHub repository URL (e.g. https://github.com/pallets/flask)

    Returns:
        Indented file tree as plain text, with AST symbols and doc hints inline.
    """
    payload: dict = {"repo_url": repo_url, "query": ""}

    vcs = _vcs_block()
    if vcs:
        payload["vcs"] = vcs

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.post(f"{API_URL}/v1/skeleton", headers=_headers(), json=payload)

        if resp.status_code == 401:
            return (
                "Error: Unauthorized. Set CONTEXTPACKER_API_KEY environment variable.\n"
                "Get a free key at https://contextpacker.com"
            )
        if resp.status_code == 404:
            return f"Error: Repository not found or is private. If private, set GITHUB_PAT.\nURL: {repo_url}"
        if not resp.is_success:
            return f"API error {resp.status_code}: {resp.text[:500]}"

        data = resp.json()
        tree = data.get("tree", "")
        stats = data.get("stats", {})

        header = (
            f"# Repository skeleton: {repo_url}\n"
            f"# {stats.get('files_considered', '?')} files indexed\n\n"
        )
        return header + tree

    except httpx.TimeoutException:
        return "Error: Request timed out. Try again — large repos take longer on first load."
    except httpx.RequestError as e:
        return f"Error: Could not reach ContextPacker API at {API_URL}.\nDetails: {e}"


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    if not API_KEY and API_URL == "https://contextpacker.com":
        print(
            "Warning: CONTEXTPACKER_API_KEY not set.\n"
            "  • Hosted API requires a key: https://contextpacker.com\n"
            "  • Self-hosted: set CONTEXTPACKER_API_URL=http://localhost:8000\n",
            file=sys.stderr,
        )
    mcp.run()
