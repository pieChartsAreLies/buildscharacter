"""Substack client for newsletter operations.

Uses python-substack (reverse-engineered, fragile). All operations include
fallback behavior: if the Substack API fails, drafts are saved to Obsidian
and a Telegram alert is sent for manual posting.

Cookies expire periodically and must be refreshed in the .env file.
"""

import hashlib
import logging

from langchain_core.tools import tool

from hobson.config import settings

logger = logging.getLogger(__name__)

_PUBLICATION_URL = "https://buildscharacter.substack.com"


def _get_api():
    """Create an authenticated Substack API client.

    Returns None if cookies are missing or expired.
    """
    if not settings.substack_cookies:
        return None
    try:
        from substack import Api

        return Api(
            cookies_string=settings.substack_cookies,
            publication_url=_PUBLICATION_URL,
        )
    except Exception as e:
        logger.warning(f"Substack auth failed: {e}")
        return None


@tool
def create_substack_draft(title: str, body_html: str, subtitle: str = "") -> str:
    """Create a draft post on Substack.

    The draft is NOT published automatically. Use publish_substack_draft
    after review, or send a Telegram notification for the owner to review
    and publish manually.

    IMPORTANT: body must be HTML, not markdown. Convert markdown to HTML
    before calling this tool. Use <p> tags for paragraphs, <h2>/<h3> for
    headings, <ul>/<li> for lists, <strong>/<em> for emphasis.

    If Substack auth fails, the draft content is returned with instructions
    to save it to Obsidian instead.

    Args:
        title: Newsletter edition title.
        body_html: Full HTML body of the newsletter.
        subtitle: Optional subtitle/preview text.
    """
    # Generate content hash for signing
    content_hash = hashlib.sha256(body_html.encode()).hexdigest()[:16]

    # Append signature to body
    signed_body = (
        f"{body_html}"
        f"<hr>"
        f"<p><em>source-sha256: {content_hash}</em></p>"
    )

    api = _get_api()
    if api is None:
        return (
            f"SUBSTACK AUTH FAILED. Save this draft to Obsidian at "
            f"'98 - Hobson Builds Character/Content/Substack/Drafts/' and "
            f"alert the owner via Telegram for manual posting.\n\n"
            f"Title: {title}\n"
            f"Subtitle: {subtitle}\n"
            f"Content hash: {content_hash}\n"
            f"Body length: {len(body_html)} chars"
        )

    try:
        draft_body = {"title": title, "body": signed_body, "type": "newsletter"}
        if subtitle:
            draft_body["subtitle"] = subtitle

        result = api.post_draft(draft_body)
        draft_id = result.get("id", "unknown")

        return (
            f"Draft created on Substack: ID {draft_id}\n"
            f"Title: {title}\n"
            f"Content hash: {content_hash}\n"
            f"Status: draft (not published). Review at {_PUBLICATION_URL}/publish/post/{draft_id}"
        )
    except Exception as e:
        return (
            f"SUBSTACK API ERROR: {e}\n"
            f"Save draft to Obsidian and alert owner via Telegram.\n"
            f"Title: {title}\n"
            f"Content hash: {content_hash}"
        )


@tool
def publish_substack_draft(draft_id: str) -> str:
    """Publish a Substack draft, sending it to all subscribers.

    IMPORTANT: Always request Telegram approval before publishing.
    This sends an email to all subscribers and cannot be undone.

    Args:
        draft_id: The draft ID from create_substack_draft.
    """
    api = _get_api()
    if api is None:
        return (
            "SUBSTACK AUTH FAILED. Cannot publish. "
            "Alert the owner via Telegram to publish manually."
        )

    try:
        api.publish_draft(draft_id, send=True)
        return f"Published draft {draft_id}. Newsletter sent to all subscribers."
    except Exception as e:
        return (
            f"SUBSTACK PUBLISH ERROR: {e}\n"
            f"Alert the owner via Telegram to publish draft {draft_id} manually."
        )


@tool
def get_substack_posts(limit: int = 10) -> str:
    """List recently published Substack posts.

    Use this to check what's already been published and avoid duplicate
    topics in the weekly edition.

    Args:
        limit: Number of posts to return (default 10).
    """
    api = _get_api()
    if api is None:
        return (
            "SUBSTACK AUTH FAILED. Cannot retrieve posts. "
            "Check if cookies need refreshing."
        )

    try:
        posts = api.get_published_posts(limit=limit)
        if not posts:
            return "No published posts yet."

        lines = [f"Last {min(limit, len(posts))} published posts:"]
        for p in posts[:limit]:
            title = p.get("title", "Untitled")
            slug = p.get("slug", "")
            pub_date = p.get("post_date", "")[:10]
            lines.append(f"  - [{pub_date}] {title} ({_PUBLICATION_URL}/p/{slug})")

        return "\n".join(lines)
    except Exception as e:
        return f"SUBSTACK API ERROR: {e}. Cookies may need refreshing."
