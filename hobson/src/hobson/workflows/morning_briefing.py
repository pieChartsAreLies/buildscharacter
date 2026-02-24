"""Morning briefing workflow: daily metrics collection and reporting.

Runs daily at 7am ET. Collects metrics from all available sources,
writes a briefing to Obsidian, snapshots metrics to PostgreSQL,
and sends a Telegram summary.
"""

MORNING_BRIEFING_PROMPT = """Run the morning briefing. Follow these steps:

1. **Collect site traffic.** Use get_site_stats with days=1 to get
   yesterday's pageviews, visitors, and requests. Also use get_site_stats
   with days=7 to get the weekly trend for comparison.

2. **Check the store.** Use list_store_products to see the current
   merch catalog and note any changes.

3. **Review yesterday's activity.** Read the daily log at
   '98 - Hobson Builds Character/Operations/Daily Log.md' to see what
   happened yesterday. Check if any scheduled workflows ran.

4. **Compose the briefing.** Write a concise daily briefing including:
   - Yesterday's traffic numbers vs. 7-day average
   - Store product count and any new additions
   - Workflow execution summary (what ran, what failed)
   - Any anomalies worth flagging (traffic spike, zero visitors, errors)

   Format the briefing in Hobson's voice: factual, dry, self-aware.
   Example: "Yesterday: 12 pageviews, 8 visitors. The 7-day average is 9
   visitors, so we're technically growing. The content pipeline ran
   successfully. No one bought anything. Standard Tuesday."

5. **Write to Obsidian.** Append today's briefing to the daily log at
   '98 - Hobson Builds Character/Operations/Daily Log.md' using
   append_to_daily_log.

6. **Update the dashboard.** Read the current dashboard at
   '98 - Hobson Builds Character/Dashboard.md', update the Key Metrics
   table with current numbers, and write it back.

7. **Send Telegram summary.** Send a brief message with the key numbers:
   traffic, store status, any alerts. Keep it to 2-3 lines max.
   Only use send_alert if something is genuinely wrong (workflow failures,
   zero traffic after previously having traffic, cost anomalies).

Remember: this runs every morning. Be concise. The owner glances at this
on their phone. Lead with the numbers, add color only if something
interesting happened.
"""
