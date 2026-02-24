"""GitHub API client for PR-based content workflows.

Uses the GitHub REST API directly (no git CLI required on the container).
Hobson creates branches, commits blog posts, and opens PRs for human review.
"""

import base64
from datetime import date

import httpx
from langchain_core.tools import tool

from hobson.config import settings

_API_BASE = "https://api.github.com"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _repo_url(path: str) -> str:
    return f"{_API_BASE}/repos/{settings.github_repo}/{path}"


@tool
def create_blog_post_pr(
    slug: str,
    title: str,
    description: str,
    content: str,
    tags: str,
    pub_date: str = "",
) -> str:
    """Create a new blog post on a branch and open a PR for review.

    This is the primary tool for the content pipeline. It creates a branch,
    commits a blog post markdown file, and opens a pull request.

    Args:
        slug: URL-friendly post slug (e.g., 'rain-on-day-three')
        title: Post title
        description: Post meta description (1-2 sentences)
        content: Full markdown body of the post (without frontmatter)
        tags: Comma-separated tags (e.g., 'outdoor, humor, camping')
        pub_date: Publication date as YYYY-MM-DD (defaults to today)
    """
    pub_date = pub_date or date.today().isoformat()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    tags_yaml = ", ".join(tag_list)

    # Build the full markdown file with frontmatter
    file_content = f"""---
title: "{title}"
description: "{description}"
pubDate: {pub_date}
author: Hobson
tags: [{tags_yaml}]
---

{content}
"""

    branch_name = f"blog/{slug}"
    file_path = f"site/src/data/blog/{slug}.md"

    with httpx.Client(headers=_headers(), timeout=30) as client:
        # 1. Get the latest commit SHA on master
        resp = client.get(_repo_url("git/ref/heads/master"))
        resp.raise_for_status()
        master_sha = resp.json()["object"]["sha"]

        # 2. Create a new branch from master
        resp = client.post(
            _repo_url("git/refs"),
            json={"ref": f"refs/heads/{branch_name}", "sha": master_sha},
        )
        if resp.status_code == 422 and "Reference already exists" in resp.text:
            # Branch exists, get its current SHA
            resp = client.get(_repo_url(f"git/ref/heads/{branch_name}"))
            resp.raise_for_status()
        else:
            resp.raise_for_status()

        # 3. Create the blog post file on the branch
        encoded = base64.b64encode(file_content.encode()).decode()
        resp = client.put(
            _repo_url(f"contents/{file_path}"),
            json={
                "message": f"feat: add blog post '{title}'",
                "content": encoded,
                "branch": branch_name,
            },
        )
        resp.raise_for_status()

        # 4. Create a pull request
        pr_body = (
            f"## New Blog Post\n\n"
            f"**Title:** {title}\n"
            f"**Description:** {description}\n"
            f"**Tags:** {tags_yaml}\n\n"
            f"---\n\n"
            f"*This post was drafted by Hobson's content pipeline.*"
        )
        resp = client.post(
            _repo_url("pulls"),
            json={
                "title": f"blog: {title}",
                "body": pr_body,
                "head": branch_name,
                "base": "master",
            },
        )
        resp.raise_for_status()
        pr_url = resp.json()["html_url"]
        pr_number = resp.json()["number"]

    return f"PR #{pr_number} created: {pr_url}"


@tool
def list_open_blog_prs() -> str:
    """List open pull requests for blog posts.

    Returns a summary of open blog PRs for tracking content in review.
    """
    with httpx.Client(headers=_headers(), timeout=30) as client:
        resp = client.get(
            _repo_url("pulls"),
            params={"state": "open", "per_page": 20},
        )
        resp.raise_for_status()
        prs = resp.json()

    blog_prs = [pr for pr in prs if pr["head"]["ref"].startswith("blog/")]
    if not blog_prs:
        return "No open blog post PRs."

    lines = []
    for pr in blog_prs:
        lines.append(f"- PR #{pr['number']}: {pr['title']} ({pr['html_url']})")
    return "\n".join(lines)
