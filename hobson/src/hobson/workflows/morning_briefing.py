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

4. **Check pending approvals.** Call get_pending_approvals to retrieve
   any unresolved approval requests. Note how many there are and whether
   any are older than 24 hours (compare created_at to today's date).

5. **Compose the briefing.** Write a concise daily briefing including:
   - Yesterday's traffic numbers vs. 7-day average
   - Store product count and any new additions
   - Workflow execution summary (what ran, what failed)
   - Pending approval count and any stale requests
   - Any anomalies worth flagging (traffic spike, zero visitors, errors)

   Format the briefing in Hobson's voice: factual, dry, self-aware.
   Example: "Yesterday: 12 pageviews, 8 visitors. The 7-day average is 9
   visitors, so we're technically growing. The content pipeline ran
   successfully. No one bought anything. Standard Tuesday."

6. **Write to Obsidian.** Append today's briefing to the daily log at
   '98 - Hobson Builds Character/Operations/Daily Log.md' using
   append_to_daily_log.

7. **Update the dashboard.** Read the current dashboard at
   '98 - Hobson Builds Character/Dashboard.md', update the Key Metrics
   table with current numbers, and write it back.

8. **Send the daily digest via Telegram.** Use send_message to send a
   structured morning digest. This is NOT a 2-line summary -- it is the
   owner's primary morning status report. Format it exactly like this:

   MORNING DIGEST -- [today's date, e.g. 2026-02-26]

   SCHEDULE TODAY:
   [List today's scheduled workflows and times. Determine the day of
   the week from today's date and use the BOOTSTRAP schedule below:
   - Every day: Morning Briefing 7:00 AM, Content Pipeline 8:00 AM,
     Content Pipeline 1:00 PM, Design Batch 2:00 PM,
     Content Pipeline 6:00 PM, Bootstrap Diary 9:00 PM
   - Friday also: Substack Dispatch 3:00 PM
   - Sunday also: Business Review 6:00 PM
   All times ET. List only the workflows that run on today's day.]

   PENDING APPROVALS:
   [List each pending approval: action, reasoning, and age.
   If none, say "None -- all clear."]

   YESTERDAY'S OUTPUT:
   [Summarize from yesterday's daily log and workflow runs:
   blog posts published (count and titles if any), products created,
   designs generated, failed workflows. If nothing happened, say so.]

   NEEDS YOUR ATTENTION:
   [Flag these if present:
   - Approval requests older than 24 hours (stale)
   - Traffic anomalies (zero visitors, unusual spikes or drops vs. 7-day avg)
   - Failed workflow runs from yesterday
   - Any other operational issues found during collection
   If nothing needs attention, say "Nothing -- smooth sailing."]

   Keep the digest factual. No filler. The owner reads this on their
   phone first thing in the morning.

   Additionally, use send_alert (not send_message) ONLY if something is
   genuinely broken: workflow circuit breakers tripped, zero traffic after
   previously having traffic, or cost anomalies. The alert is separate
   from the digest.

Remember: this runs every morning at 7am ET. The digest is the main
deliverable. The Obsidian log and dashboard updates are important but
the owner sees the Telegram message first.
"""
