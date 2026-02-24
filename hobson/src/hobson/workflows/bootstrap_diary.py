"""Bootstrap diary workflow: daily operational summary post.

Runs at 9pm ET during bootstrap mode only. Writes a short, raw operational
summary of the day's activities and publishes it as a blog post. This turns
the bootstrap process itself into compelling content for HN/Reddit audiences.
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
   - Raw and operational, not polished prose
   - Real numbers, real failures, no sugarcoating
   - Dry humor when it fits naturally
   - This is a build log, not a blog post -- keep it tight

4. **Publish the diary entry.** Use publish_blog_post with:
   - slug: 'bootstrap-diary-day-N' (where N is the sprint day number,
     calculate from the first diary entry or start at 1)
   - title: "Bootstrap Diary: Day N"
   - description: A one-line summary of the day
   - tags: "bootstrap, diary, transparency, meta"
   - The full diary content as the body

5. **Update the content calendar.** Append the diary entry to the content
   calendar noting it as published.

6. **Notify via Telegram.** Send a short message: "Bootstrap Diary Day N
   published. Current progress: X/10 posts, Y/15 products."

Remember: this diary IS the content the HN/Reddit audience will find most
interesting. An AI agent narrating its own bootstrap process in real-time
is the story that drives traffic.
"""
