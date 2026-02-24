"""Obsidian REST API client for vault operations."""

from datetime import date

import httpx
from langchain_core.tools import tool

from hobson.config import settings

_BASE_URL = f"https://{settings.obsidian_host}:{settings.obsidian_port}"
_HEADERS = {"Authorization": f"Bearer {settings.obsidian_api_key}"}


def _client() -> httpx.Client:
    return httpx.Client(base_url=_BASE_URL, headers=_HEADERS, timeout=30, verify=False)


@tool
def write_note(path: str, content: str) -> str:
    """Write or overwrite a note in the Obsidian vault.

    Args:
        path: Vault-relative path (e.g., '98 - Hobson Builds Character/Operations/Daily Log.md')
        content: Full markdown content for the note
    """
    with _client() as client:
        resp = client.put(f"/vault/{path}", content=content, headers={"Content-Type": "text/markdown"})
        resp.raise_for_status()
    return f"Wrote note: {path}"


@tool
def read_note(path: str) -> str:
    """Read a note from the Obsidian vault.

    Args:
        path: Vault-relative path (e.g., '98 - Hobson Builds Character/Dashboard.md')
    """
    with _client() as client:
        resp = client.get(f"/vault/{path}", headers={"Accept": "text/markdown"})
        if resp.status_code == 404:
            return f"Note not found: {path}"
        resp.raise_for_status()
    return resp.text


@tool
def append_to_note(path: str, content: str) -> str:
    """Append content to an existing note in the Obsidian vault.

    Args:
        path: Vault-relative path
        content: Markdown content to append
    """
    with _client() as client:
        resp = client.post(
            f"/vault/{path}",
            content=content,
            headers={"Content-Type": "text/markdown"},
        )
        resp.raise_for_status()
    return f"Appended to note: {path}"


@tool
def append_to_daily_log(entry: str) -> str:
    """Append an entry to today's section in the Hobson daily log.

    Args:
        entry: A single log entry line (will be prefixed with '- ')
    """
    today = date.today().isoformat()
    log_path = "98 - Hobson Builds Character/Operations/Daily Log.md"

    with _client() as client:
        # Read current content
        resp = client.get(f"/vault/{log_path}", headers={"Accept": "text/markdown"})
        current = resp.text if resp.status_code == 200 else ""

        # Check if today's section exists
        if f"## {today}" not in current:
            addition = f"\n## {today}\n- {entry}\n"
        else:
            addition = f"- {entry}\n"

        resp = client.post(
            f"/vault/{log_path}",
            content=addition,
            headers={"Content-Type": "text/markdown"},
        )
        resp.raise_for_status()
    return f"Logged to daily log: {entry}"


@tool
def list_vault_folder(path: str) -> str:
    """List files in a vault folder.

    Args:
        path: Vault-relative folder path (e.g., '98 - Hobson Builds Character/Content/Blog/Drafts')
    """
    with _client() as client:
        resp = client.get(f"/vault/{path}/")
        if resp.status_code == 404:
            return "[]"
        resp.raise_for_status()
    return resp.text
