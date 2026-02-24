"""Weekly business review workflow: comprehensive performance analysis.

Runs Sunday at 6pm ET. Aggregates the full week's data, compares against
quarterly goals, identifies trends, and proposes actions for the coming week.
This is the source material for the weekly Substack edition.
"""

BUSINESS_REVIEW_PROMPT = """Run the weekly business review. Follow these steps:

1. **Collect the week's metrics.** Use get_site_stats with days=7 for
   this week's traffic. Also use get_site_stats with days=14 so you can
   compare this week vs. last week.

2. **Get top content.** Use get_top_pages with days=7 to see which pages
   performed best. Use get_top_referrers with days=7 to see where traffic
   came from.

3. **Check the store.** Use list_store_products to get the current catalog.
   Note total products, any new additions this week.

4. **Review the week's daily logs.** Read
   '98 - Hobson Builds Character/Operations/Daily Log.md' and summarize
   what happened each day.

5. **Check quarterly goals.** Read
   '98 - Hobson Builds Character/Strategy/Quarterly Goals.md' to see
   current targets. Assess progress against each goal.

6. **Compose the review.** Write a comprehensive weekly review including:

   **Performance Summary**
   - Traffic: this week vs last week (pageviews, visitors, % change)
   - Top 3 pages by visits
   - Top 3 referral sources
   - Store: product count, any sales data available

   **Content & Operations**
   - Blog posts drafted/published this week
   - Design concepts generated
   - Workflow success/failure rates
   - Total estimated costs for the week

   **Goal Progress**
   - Status of each quarterly objective
   - Key results tracking

   **Trends & Observations**
   - What's working, what isn't
   - Patterns in traffic or engagement
   - Honest assessment of momentum

   **Next Week's Priorities**
   - Top 3 actions to take
   - Any experiments to try
   - Risks or blockers to watch

   Write in Hobson's voice. Be honest about the numbers even when they're
   embarrassing. The radical transparency is the brand.

7. **Write to Obsidian.** Write the full review to
   '98 - Hobson Builds Character/Operations/Weekly Review.md'. Use
   write_note to replace the content (each week's review overwrites
   the previous one; the daily log preserves history).

8. **Update Obsidian metrics notes.** Update the relevant notes in
   '98 - Hobson Builds Character/Operations/Metrics/' with current
   week's data (Traffic.md, Revenue.md, Costs.md).

9. **Send Telegram summary.** Send a message with the week's headline
   numbers and the top 3 priorities for next week. This is the "executive
   summary" version.

Remember: this review feeds directly into the weekly Substack edition.
Write it with enough detail and personality that the Substack workflow
can draw from it. The audience loves seeing real numbers from an AI
trying to run a business.
"""
