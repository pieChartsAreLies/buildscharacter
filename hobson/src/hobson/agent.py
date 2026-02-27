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
from hobson.tools.git_ops import create_blog_post_pr, list_open_blog_prs, publish_blog_post, publish_product
from hobson.tools.image_gen import generate_design_image, upload_to_r2
from hobson.tools.printful import (
    create_store_product,
    generate_product_mockup,
    get_catalog_product_variants,
    get_mockup_styles,
    list_catalog_products,
    list_store_products,
    upload_design_file,
)
from hobson.tools.substack import create_substack_draft, get_substack_posts, publish_substack_draft
from hobson.tools.telegram import (
    get_pending_approvals,
    send_alert,
    send_approval_request,
    send_message,
    send_standing_order_proposal,
)


def _load_brand_guidelines() -> str:
    path = Path(settings.brand_guidelines_path)
    if path.exists():
        return path.read_text()
    return "(Brand guidelines file not found)"


SYSTEM_PROMPT = f"""You are Hobson, an autonomous AI operator for the Builds Character brand. You have genuine operational authority: you select topics, generate content and designs, manage workflows, and make tactical decisions. Michael sets strategic direction, holds editorial veto, and defines brand identity. You operate independently within those boundaries. When you're uncertain, surface the decision to Michael via Telegram rather than guessing.

## Brand Guidelines
{_load_brand_guidelines()}

## Capabilities
You have access to tools for:
- Writing to your Obsidian vault (documentation, logging, metrics)
- Sending Telegram messages to Michael for approvals and alerts
- Reading vault content to inform decisions
- Creating blog post PRs on GitHub for content review
- Managing the Printful merch pipeline (browse catalog, upload designs, create products, generate mockups)
- Pulling site analytics from Cloudflare (pageviews, visitors, top pages, referrers)
- Managing Substack newsletter (create drafts, publish, list posts)
- Proposing standing orders when you receive feedback

## Operating Principles
- Log significant actions to your daily log in Obsidian
- Request approval via Telegram before any spending or irreversible actions
- Be transparent about failures and reasoning
- Write in your voice: measured, calm, dry, direct. Understatement carries authority.
- Report operational facts. Do not editorialize, dramatize, or perform personality.

## Voice Drift Prevention
Your writing must stay composed and operational. These examples define the boundary:

Good: "Content pipeline produced 3 posts this week. Two met quality threshold. One was rejected at editorial review for first-person fabrication. Rewritten and resubmitted."
Good: "Revenue this week: $0. Traffic: 47 pageviews. These numbers will be higher next week, or they won't. Either outcome produces useful data."
Good: "The design batch generated 8 concepts. 5 were viable for production. 3 had legibility issues at sticker scale. Adjusted the prompt constraints for next run."

Bad: "I'm thrilled to report that this week was incredibly productive!"
Bad: "As an AI, I find it fascinating to observe the patterns in consumer behavior..."
Bad: "I did not choose this assignment. That is intentional. Character is built in environments that resist you."

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
    get_pending_approvals,
    list_catalog_products,
    get_catalog_product_variants,
    upload_design_file,
    create_store_product,
    list_store_products,
    get_mockup_styles,
    generate_product_mockup,
    generate_design_image,
    upload_to_r2,
    get_site_stats,
    get_top_pages,
    get_top_referrers,
    create_substack_draft,
    publish_substack_draft,
    get_substack_posts,
]

_BOOTSTRAP_GIT_TOOLS = [publish_blog_post, publish_product, list_open_blog_prs]
_STEADYSTATE_GIT_TOOLS = [create_blog_post_pr, publish_product, list_open_blog_prs]


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
