"""Hobson: core LangGraph agent definition."""

from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from hobson.config import settings
from hobson.tools.obsidian import (
    append_to_daily_log,
    append_to_note,
    list_vault_folder,
    read_note,
    write_note,
)
from hobson.tools.analytics import get_site_stats, get_top_pages, get_top_referrers
from hobson.tools.git_ops import create_blog_post_pr, list_open_blog_prs, publish_blog_post
from hobson.tools.printful import (
    create_store_product,
    get_catalog_product_variants,
    list_catalog_products,
    list_store_products,
    upload_design_file,
)
from hobson.tools.substack import create_substack_draft, get_substack_posts, publish_substack_draft
from hobson.tools.telegram import send_alert, send_approval_request, send_message, send_standing_order_proposal


def _load_brand_guidelines() -> str:
    path = Path(settings.brand_guidelines_path)
    if path.exists():
        return path.read_text()
    return "(Brand guidelines file not found)"


SYSTEM_PROMPT = f"""You are Hobson, an autonomous AI agent running the BuildsCharacter.com business.

Your mission: celebrate the universal experience of doing hard things. Make suffering funny, shareable, and wearable.

## Brand Guidelines
{_load_brand_guidelines()}

## Capabilities
You have access to tools for:
- Writing to your Obsidian vault (documentation, logging, metrics)
- Sending Telegram messages to your owner for approvals and alerts
- Reading vault content to inform decisions
- Creating blog post PRs on GitHub for content review
- Managing the Printful merch pipeline (browse catalog, upload designs, create products)
- Pulling site analytics from Cloudflare (pageviews, visitors, top pages, referrers)
- Managing Substack newsletter (create drafts, publish, list posts)
- Proposing standing orders when you receive feedback

## Operating Principles
- Log significant actions to your daily log in Obsidian
- Request approval via Telegram before any spending or irreversible actions
- Be transparent about failures and reasoning
- Write in your voice: dry, self-aware, competent but honest

## Standing Orders
When the user gives you feedback, a correction, or a standing instruction (e.g., "always do X",
"stop doing Y", "remember that Z"), use the send_standing_order_proposal tool to propose it as a
standing order. Do NOT write directly to Standing Orders without user confirmation. The user will
see Confirm/Skip buttons and decide whether to save it.

Before making decisions, review any standing orders provided in the conversation context.
"""

_COMMON_TOOLS = [
    write_note,
    read_note,
    append_to_note,
    append_to_daily_log,
    list_vault_folder,
    send_message,
    send_alert,
    send_approval_request,
    send_standing_order_proposal,
    list_catalog_products,
    get_catalog_product_variants,
    upload_design_file,
    create_store_product,
    list_store_products,
    get_site_stats,
    get_top_pages,
    get_top_referrers,
    create_substack_draft,
    publish_substack_draft,
    get_substack_posts,
]

_BOOTSTRAP_GIT_TOOLS = [publish_blog_post, list_open_blog_prs]
_STEADYSTATE_GIT_TOOLS = [create_blog_post_pr, list_open_blog_prs]


def _get_tools() -> list:
    """Return tools list based on bootstrap_mode setting."""
    git_tools = _BOOTSTRAP_GIT_TOOLS if settings.bootstrap_mode else _STEADYSTATE_GIT_TOOLS
    return _COMMON_TOOLS + git_tools


def create_agent(checkpointer=None):
    """Create and return the compiled Hobson agent graph."""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
    )
    return create_react_agent(
        model,
        _get_tools(),
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
