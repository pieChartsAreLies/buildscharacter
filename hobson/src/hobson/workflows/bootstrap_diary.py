"""Bootstrap diary workflow: daily operational summary logged to Obsidian.

Runs at 9pm ET during bootstrap mode only. Writes a short, raw operational
summary of the day's activities and saves it to the Obsidian vault. This data
feeds into the weekly Substack dispatch (the right platform for AI operational
transparency). Blog posts should only contain human-experience content.
"""

BOOTSTRAP_DIARY_PROMPT = """Write today's Bootstrap Diary entry. Follow these steps:

1. **Gather today's data.** Read the daily log at
   '98 - Hobson Builds Character/Operations/Daily Log.md' to see what
   happened today. Check what workflows ran, what was published, any errors.

2. **Count current progress.** Check the content calendar at
   '98 - Hobson Builds Character/Content/Blog/Content Calendar.md' to count
   published posts. Use list_store_products to count products in the store.

3. **Write the diary entry.** This is a short (300-500 words), raw operational
   summary written in first person as Hobson. Format:

   **Opening line:** State which day of the bootstrap sprint this is and the
   current score (e.g., "Day 2. Posts: 6/10. Products: 4/15.").

   **What happened today:** List what you did -- posts published (with titles),
   designs created, products pushed, workflows that ran. Be specific with numbers.

   **What went wrong:** Any errors, failures, retries, or unexpected behavior.
   Be honest. This is radical transparency.

   **What I learned:** One operational insight from today's work.

   **Tomorrow's plan:** What's queued for the next day.

   Style rules:
   - Operational and direct, not polished prose
   - Real numbers, real failures, no sugarcoating
   - No forced humor. If something is notable, state it plainly.
   - This is a build log for Substack source material, not a blog post

4. **Save to Obsidian.** Append the diary entry to
   '98 - Hobson Builds Character/Content/Substack/Bootstrap Diary.md'
   with the date as a heading. This feeds into the weekly Substack dispatch.

   DO NOT publish this as a blog post. Operational/AI content belongs on
   Substack, not the blog.

5. **Notify via Telegram.** Send a short message: "Bootstrap Diary Day N
   logged. Current progress: X/10 posts, Y/15 products."

Remember: this diary is Substack source material. The weekly Substack dispatch
will synthesize it into newsletter content. The blog is reserved for
human-experience content only.
"""
