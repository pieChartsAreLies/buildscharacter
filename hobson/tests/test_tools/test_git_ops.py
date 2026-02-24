"""Tests for blog post validation logic in git_ops.

The validation function is duplicated here to avoid importing hobson.tools.git_ops
directly, which pulls in pydantic_settings and other dependencies that aren't
installed in the local dev environment (the project runs on CT 255).
"""

import re

# --- Copied from hobson/src/hobson/tools/git_ops.py --------------------------
# Keep in sync with the source. If the validation logic changes there, update here.

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _validate_blog_post(
    slug: str,
    title: str,
    description: str,
    content: str,
    tags: str,
) -> list[str]:
    """Validate blog post fields before publishing."""
    errors: list[str] = []

    if not _SLUG_RE.match(slug):
        errors.append(
            f"Slug '{slug}' is not URL-safe "
            "(must match ^[a-z0-9]+(?:-[a-z0-9]+)*$)"
        )

    if not title.strip():
        errors.append("Title is empty")

    if not description.strip():
        errors.append("Description is empty")

    if not tags.strip():
        errors.append("Tags is empty")

    word_count = len(content.split())
    if word_count < 250:
        errors.append(
            f"Content body has {word_count} words (minimum 250 required)"
        )

    return errors


# --- End copy -----------------------------------------------------------------


def _make_long_content(word_count: int = 300) -> str:
    """Generate placeholder content with the given word count."""
    return " ".join(["word"] * word_count)


class TestValidateBlogPost:
    """Tests for _validate_blog_post pre-flight checks."""

    def test_valid_post_passes(self):
        errors = _validate_blog_post(
            slug="rain-on-day-three",
            title="Rain on Day Three",
            description="A story about rain during a camping trip.",
            content=_make_long_content(300),
            tags="outdoor, humor, camping",
        )
        assert errors == []

    def test_invalid_slug_uppercase(self):
        errors = _validate_blog_post(
            slug="Rain-On-Day-Three",
            title="Rain on Day Three",
            description="A story about rain.",
            content=_make_long_content(300),
            tags="outdoor",
        )
        assert len(errors) == 1
        assert "Slug" in errors[0]
        assert "URL-safe" in errors[0]

    def test_invalid_slug_special_chars(self):
        errors = _validate_blog_post(
            slug="rain_on_day!three",
            title="Rain on Day Three",
            description="A story about rain.",
            content=_make_long_content(300),
            tags="outdoor",
        )
        assert len(errors) == 1
        assert "Slug" in errors[0]

    def test_empty_title_caught(self):
        errors = _validate_blog_post(
            slug="valid-slug",
            title="",
            description="A description.",
            content=_make_long_content(300),
            tags="outdoor",
        )
        assert len(errors) == 1
        assert "Title is empty" in errors[0]

    def test_short_content_caught(self):
        errors = _validate_blog_post(
            slug="valid-slug",
            title="A Title",
            description="A description.",
            content="Only a few words here.",
            tags="outdoor",
        )
        assert len(errors) == 1
        assert "250" in errors[0]
        assert "words" in errors[0]

    def test_empty_tags_caught(self):
        errors = _validate_blog_post(
            slug="valid-slug",
            title="A Title",
            description="A description.",
            content=_make_long_content(300),
            tags="",
        )
        assert len(errors) == 1
        assert "Tags is empty" in errors[0]

    def test_multiple_errors_returned(self):
        """All failures are reported at once, not just the first."""
        errors = _validate_blog_post(
            slug="BAD SLUG!",
            title="",
            description="",
            content="short",
            tags="",
        )
        assert len(errors) == 5
