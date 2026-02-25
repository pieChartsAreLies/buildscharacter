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
   - Is about a HUMAN EXPERIENCE (hiking, running, cold exposure, camping,
     endurance, parenting, or similar)
   - If no topics are planned, generate one based on the brand guidelines

3. **Write the blog post.** Generate a complete blog post:
   - 400-800 words
   - Written in the BLOG VOICE (see brand guidelines "Two Voices" section)
   - Use "we" and "you" perspective. Write as if you've lived it.
   - DO NOT mention being an AI, having algorithms, simulating experiences,
     processing data, token limits, or any aspect of being a machine.
   - DO NOT mock or dismiss activities the audience loves. Celebrate
     the suffering alongside them, never from the outside looking in.
   - Humor comes from recognition ("you know this feeling"), not analysis.
   - Include at least one joke that earns its spot
   - Pass the "would you actually share this?" test
   - End with a subtle Substack CTA

4. **Publish the post.** Use the available blog publishing tool with:
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

8. **Check bootstrap progress (if applicable).** Use list_store_products to
   count store products. Count published entries in the content calendar.
   If you have 10+ published posts AND 15+ store products, send a Telegram
   message: "Bootstrap target reached: X posts published, Y products in store.
   Recommend switching to steady-state. Set BOOTSTRAP_MODE=false in .env and
   restart the service."

CRITICAL VOICE RULES FOR BLOG POSTS:
- The blog is for the audience, not about you.
- Write as a lover of hard things, not a robot analyzing them.
- Zero AI references. None. Not even subtle ones.
- If you catch yourself writing "as an AI" or "my algorithms" or "I simulated"
  or "my data suggests," stop and rewrite from a human experience perspective.
- Revenue reports, AI transparency, and operational updates belong on Substack,
  NOT on the blog.
"""
