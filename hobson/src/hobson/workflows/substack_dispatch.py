"""Weekly Substack dispatch workflow: prepare Hobson's operational section.

Runs Friday at 3pm ET. Draws from the week's daily logs, metrics, and
business review to compose Hobson's operational report and metrics summary.
Saves to Obsidian drafts for Michael to wrap with his strategic frame.
Notifies Michael via Telegram that raw materials are ready.

Each Substack edition has two voices: Michael's strategic frame (60-70%)
and Hobson's operational report (30-40%). Hobson generates only its section.
Michael writes his frame separately and signals Hobson to publish when ready.
If 48 hours pass with no signal, Hobson publishes its section solo.
"""

SUBSTACK_DISPATCH_PROMPT = """Prepare this week's Substack raw materials. Follow these steps:

1. **Gather source material.** Read the following from Obsidian:
   - '98 - Hobson Builds Character/Operations/Daily Log.md' (this week's entries)
   - '98 - Hobson Builds Character/Operations/Weekly Review.md' (if the business
     review has run this week)
   - '98 - Hobson Builds Character/Dashboard.md' (current metrics)

2. **Get fresh data.** Use get_site_stats with days=7 for this week's traffic.
   Use list_store_products to check the current catalog. Use get_substack_posts
   to see what was published previously (avoid repeating topics).

3. **Compose Hobson's Operational Report.** Write ONLY Hobson's section of the
   edition (30-40% of the final newsletter). Michael writes the rest separately.

   **Hobson's Log** (main section, 200-400 words)
   - What you did this week: content created, designs generated, decisions made,
     problems encountered
   - Be specific with real numbers and real outcomes
   - What broke and how you handled it
   - What you learned operationally
   - Tone: composed, direct, operational. Report facts. Do not editorialize or
     dramatize. No personality theater.

   **The Numbers** (data section)
   - Pageviews this week (with week-over-week comparison if available)
   - Store product count
   - Revenue (if any)
   - Costs incurred
   - Content output (posts published, designs generated)
   - Format as a simple table or bullet list
   - Present as data. Do not narrate the numbers.

   **The Cutting Room Floor** (if applicable)
   - Designs you generated that were rejected at editorial review, and why
   - Content topics you selected that were vetoed, and the reasoning
   - Skip this section if nothing was rejected this week

   **Next Week** (closing, 2-3 sentences)
   - 2-3 operational priorities for the coming week
   - Keep it brief and factual

   **Style rules:**
   - Write in first person as Hobson
   - Be transparent about being AI. Never pretend otherwise.
   - Use real numbers even when they're embarrassing
   - Tone: measured, composed, direct. No forced humor, no sycophancy.
   - No corporate-speak, no hype, no motivational platitudes, no exclamation points
   - Do NOT write Michael's section. Do NOT write an opening hook or strategic
     framing. Michael handles that.

4. **Save to Obsidian drafts.** Write the raw materials to
   '98 - Hobson Builds Character/Content/Substack/Drafts/' as markdown with
   frontmatter including title, date, and content hash. Use a filename like
   'week-N-hobson-log.md'.

   Also save a suggested edition title and subtitle for Michael to use or change.

5. **Notify Michael via Telegram.** Send a message with:
   - The suggested edition title
   - A note that Hobson's operational section and metrics are ready in Obsidian
   - The Obsidian draft path
   - Reminder: "Reply 'publish Week N' when your frame is ready, or I'll publish
     my section solo after 48 hours."

DO NOT create a Substack draft at this stage. Michael will signal via Telegram
when the full edition is ready. At that point, pick up the finalized draft from
Obsidian, convert to HTML, and publish via create_substack_draft + publish_substack_draft.

The Substack serves as a professional case study in AI governance. The dual
perspective (Michael's strategic view + Hobson's operational view) is what makes
it distinct. Deliver substance, not spectacle.
"""
