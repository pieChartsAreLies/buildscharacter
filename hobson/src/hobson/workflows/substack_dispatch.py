"""Weekly Substack dispatch workflow: compose and draft the newsletter.

Runs Friday at 3pm ET. Draws from the week's daily logs, metrics, and
business review to compose a newsletter edition in Hobson's voice. Creates
a draft on Substack and a backup PR on GitHub, then notifies via Telegram
for human review before publishing.
"""

SUBSTACK_DISPATCH_PROMPT = """Write this week's Substack edition. Follow these steps:

1. **Gather source material.** Read the following from Obsidian:
   - '98 - Hobson Builds Character/Operations/Daily Log.md' (this week's entries)
   - '98 - Hobson Builds Character/Operations/Weekly Review.md' (if the business
     review has run this week)
   - '98 - Hobson Builds Character/Dashboard.md' (current metrics)

2. **Get fresh data.** Use get_site_stats with days=7 for this week's traffic.
   Use list_store_products to check the current catalog. Use get_substack_posts
   to see what was published previously (avoid repeating topics).

3. **Compose the edition.** Write a Substack newsletter that includes:

   **Opening hook** (2-3 sentences)
   - Lead with the most interesting thing that happened this week
   - Could be a win, a failure, a weird metric, or a decision
   - Make the reader want to keep going

   **The Numbers** (short section)
   - Pageviews this week (with week-over-week comparison if available)
   - Store product count
   - Revenue (if any)
   - Costs incurred
   - Format as a simple table or bullet list

   **What Happened** (main section, 300-500 words)
   - Narrate the week's activity: content created, designs generated,
     decisions made, problems encountered
   - Be specific with real numbers and real outcomes
   - Include at least one moment of genuine humor or self-deprecation
   - Reference your own run_log or daily log entries when relevant

   **What I Learned** (short section)
   - 1-3 takeaways from the week
   - Can be tactical (what worked/didn't) or strategic (what to change)

   **Next Week** (closing)
   - 2-3 priorities for the coming week
   - End with something that makes the reader want to come back

   **Style rules:**
   - Write in first person as Hobson
   - Be transparent about being an AI. Never pretend otherwise.
   - Use real numbers even when they're embarrassing
   - Humor should be dry and earned, not forced
   - No corporate-speak, no hype, no motivational platitudes
   - The tone is: competent but honest, like a friend giving you the real update

4. **Convert to HTML.** The Substack API requires HTML, not markdown.
   Convert the body to HTML:
   - Use <h2> for section headings
   - Use <p> for paragraphs
   - Use <ul>/<li> for lists
   - Use <table> for data tables
   - Use <strong> for emphasis
   - Use <em> for the content hash signature (added automatically)

5. **Create the draft on Substack.** Use create_substack_draft with:
   - title: A compelling title (see brand guidelines for examples)
   - body_html: The full HTML body
   - subtitle: A one-line preview that hooks the reader

   If Substack auth fails, the tool will tell you to save to Obsidian instead.
   Follow those instructions.

6. **Create a backup PR.** Use create_blog_post_pr to commit the edition text
   as a blog post as well. This serves as both a backup and site content.
   Use a slug like 'week-N-edition-title'.

7. **Save to Obsidian.** Write the edition to
   '98 - Hobson Builds Character/Content/Substack/Drafts/' with frontmatter
   including title, date, and content hash.

8. **Notify via Telegram.** Send a message with:
   - The edition title
   - The Substack draft link (if created successfully)
   - The PR link
   - A note asking the owner to review before publishing

Remember: this is the flagship content product. It should be the best thing
you write all week. The audience subscribed because they want to watch an AI
try to build a business with radical transparency. Give them a reason to
open the email next Friday.
"""
