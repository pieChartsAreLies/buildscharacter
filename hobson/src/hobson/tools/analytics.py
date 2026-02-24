"""Cloudflare Analytics client for site traffic data.

Uses the Cloudflare GraphQL Analytics API (free tier) to pull pageviews,
visitors, top pages, and referrers for buildscharacter.com. No additional
service to deploy -- the domain is already on Cloudflare.
"""

from datetime import date, timedelta

import httpx
from langchain_core.tools import tool

from hobson.config import settings

_GQL_ENDPOINT = "https://api.cloudflare.com/client/v4/graphql"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.cloudflare_api_token}",
        "Content-Type": "application/json",
    }


def _query(query: str, variables: dict) -> dict:
    """Execute a GraphQL query against the Cloudflare Analytics API."""
    with httpx.Client(headers=_headers(), timeout=30) as client:
        resp = client.post(_GQL_ENDPOINT, json={"query": query, "variables": variables})
        resp.raise_for_status()
        data = resp.json()
    if data.get("errors"):
        return {"error": str(data["errors"])}
    return data.get("data", {})


@tool
def get_site_stats(days: int = 1) -> str:
    """Get site traffic stats (pageviews, visitors, requests) for recent days.

    Pulls from Cloudflare Analytics for buildscharacter.com. Use this in
    the morning briefing to report yesterday's traffic, or with a larger
    window for weekly/monthly summaries.

    Args:
        days: Number of days to look back (default 1 = yesterday only).
    """
    end = date.today()
    start = end - timedelta(days=days)

    query = """
    query SiteStats($zoneTag: string!, $start: Date!, $end: Date!) {
      viewer {
        zones(filter: {zoneTag: $zoneTag}) {
          httpRequests1dGroups(
            filter: {date_geq: $start, date_lt: $end}
            orderBy: [date_ASC]
            limit: 31
          ) {
            dimensions { date }
            sum { pageViews requests bytes }
            uniq { uniques }
          }
        }
      }
    }
    """
    variables = {
        "zoneTag": settings.cloudflare_zone_id,
        "start": start.isoformat(),
        "end": end.isoformat(),
    }

    data = _query(query, variables)
    if "error" in data:
        return f"Analytics error: {data['error']}"

    zones = data.get("viewer", {}).get("zones", [])
    if not zones:
        return "No analytics data returned (check zone ID)."

    groups = zones[0].get("httpRequests1dGroups", [])
    if not groups:
        return f"No traffic data for {start} to {end}."

    total_pageviews = sum(g["sum"]["pageViews"] for g in groups)
    total_visitors = sum(g["uniq"]["uniques"] for g in groups)
    total_requests = sum(g["sum"]["requests"] for g in groups)

    lines = [f"Site stats for {start} to {end} ({days} day{'s' if days > 1 else ''}):",
             f"  Pageviews: {total_pageviews:,}",
             f"  Unique visitors: {total_visitors:,}",
             f"  Total requests: {total_requests:,}"]

    if days > 1 and len(groups) > 1:
        lines.append("\nDaily breakdown:")
        for g in groups:
            d = g["dimensions"]["date"]
            pv = g["sum"]["pageViews"]
            uv = g["uniq"]["uniques"]
            lines.append(f"  {d}: {pv} pageviews, {uv} visitors")

    return "\n".join(lines)


@tool
def get_top_pages(days: int = 7, limit: int = 10) -> str:
    """Get the most visited pages on the site.

    Args:
        days: Number of days to look back (default 7).
        limit: Max pages to return (default 10).
    """
    end = date.today()
    start = end - timedelta(days=days)

    query = """
    query TopPages($zoneTag: string!, $filter: ZoneHttpRequestsAdaptiveGroupsFilter_InputObject!) {
      viewer {
        zones(filter: {zoneTag: $zoneTag}) {
          httpRequestsAdaptiveGroups(
            filter: $filter
            limit: %d
            orderBy: [count_DESC]
          ) {
            count
            dimensions { clientRequestPath }
          }
        }
      }
    }
    """ % limit

    variables = {
        "zoneTag": settings.cloudflare_zone_id,
        "filter": {
            "datetime_geq": f"{start}T00:00:00Z",
            "datetime_lt": f"{end}T00:00:00Z",
            "requestSource": "eyeball",
        },
    }

    data = _query(query, variables)
    if "error" in data:
        return f"Analytics error: {data['error']}"

    zones = data.get("viewer", {}).get("zones", [])
    if not zones:
        return "No data returned."

    groups = zones[0].get("httpRequestsAdaptiveGroups", [])
    if not groups:
        return f"No page data for the last {days} days."

    lines = [f"Top {len(groups)} pages (last {days} days):"]
    for g in groups:
        path = g["dimensions"]["clientRequestPath"]
        count = g["count"]
        lines.append(f"  {count:>6,} hits  {path}")

    return "\n".join(lines)


@tool
def get_top_referrers(days: int = 7, limit: int = 10) -> str:
    """Get the top referrers driving traffic to the site.

    Args:
        days: Number of days to look back (default 7).
        limit: Max referrers to return (default 10).
    """
    end = date.today()
    start = end - timedelta(days=days)

    query = """
    query TopReferrers($zoneTag: string!, $filter: ZoneHttpRequestsAdaptiveGroupsFilter_InputObject!) {
      viewer {
        zones(filter: {zoneTag: $zoneTag}) {
          httpRequestsAdaptiveGroups(
            filter: $filter
            limit: %d
            orderBy: [count_DESC]
          ) {
            count
            dimensions { clientRefererHost }
          }
        }
      }
    }
    """ % limit

    variables = {
        "zoneTag": settings.cloudflare_zone_id,
        "filter": {
            "datetime_geq": f"{start}T00:00:00Z",
            "datetime_lt": f"{end}T00:00:00Z",
            "requestSource": "eyeball",
        },
    }

    data = _query(query, variables)
    if "error" in data:
        return f"Analytics error: {data['error']}"

    zones = data.get("viewer", {}).get("zones", [])
    if not zones:
        return "No data returned."

    groups = zones[0].get("httpRequestsAdaptiveGroups", [])
    if not groups:
        return f"No referrer data for the last {days} days."

    lines = [f"Top {len(groups)} referrers (last {days} days):"]
    for g in groups:
        referrer = g["dimensions"]["clientRefererHost"] or "(direct)"
        count = g["count"]
        lines.append(f"  {count:>6,} hits  {referrer}")

    return "\n".join(lines)
