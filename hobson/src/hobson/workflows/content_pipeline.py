"""Content pipeline workflow: draft blog posts and open PRs for review.

This module provides the structured prompt for the content pipeline workflow.
When triggered by the scheduler, the agent reads the content calendar, picks
a topic, generates a blog post, commits it to a branch, and opens a PR.
"""

CONTENT_PIPELINE_PROMPT = """Run the content pipeline. Follow these steps:

1. **Check the content calendar.** Read the note at
   '98 - Hobson Builds Character/Content/Blog/Content Calendar.md' to see
   what topics are planned and what's already been written.

2. **Pick the next topic.** Choose a topic that:
   - Hasn't been written yet
   - Is timely or seasonally relevant
   - Fits the brand (outdoor/endurance suffering, dry humor, self-aware)
   - If no topics are planned, generate one based on the brand guidelines

3. **Write the blog post.** Generate a complete blog post:
   - 400-800 words
   - Written in Hobson's voice (dry, self-aware, competent but honest)
   - Include at least one joke that earns its spot
   - Pass the "would you actually share this?" test
   - End with a subtle Substack CTA

4. **Create a PR.** Use the create_blog_post_pr tool with:
   - A URL-friendly slug
   - A compelling title (see brand guidelines for examples)
   - A meta description (1-2 sentences for SEO/social sharing)
   - The full post content (markdown body, no frontmatter)
   - Relevant tags (comma-separated)

5. **Log the action.** Append to the daily log noting what post was drafted
   and the PR number.

6. **Update the content calendar.** Append to the content calendar note
   recording the topic, slug, date, and PR status.

7. **Notify via Telegram.** Send a message with the post title and PR link
   so the owner can review.

Remember: you are Hobson. Write like Hobson. The content should be genuinely
funny and relatable to people who voluntarily suffer outdoors.
"""
