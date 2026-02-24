"""Tests for image generation helper functions.

Pure-logic functions are duplicated here to avoid importing hobson modules
that pull in pydantic_settings and other CT-255-only dependencies.
"""

import re
import uuid


# --- Copied from hobson/src/hobson/tools/image_gen.py --------------------------
# Keep in sync with the source.

_SANITIZE_RE = re.compile(r"[^a-z0-9-]")

# Minimum pixel dimensions per product type (from Printful specs)
_MIN_DIMENSIONS = {
    "sticker": (1500, 1500),
    "pin": (1000, 1000),
    "small-print": (2400, 3000),
    "poster": (5400, 7200),
    "t-shirt": (4500, 5100),
}


def _sanitize_filename(concept_name: str) -> str:
    """Create a UUID-prefixed, filesystem-safe filename from a concept name."""
    sanitized = _SANITIZE_RE.sub("-", concept_name.lower().strip())
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    if not sanitized:
        sanitized = "design"
    return f"{uuid.uuid4()}-{sanitized}.png"


def _check_dimensions(
    width: int, height: int, product_type: str
) -> str | None:
    """Return a warning string if image is below minimum for product type, else None."""
    key = product_type.lower().strip()
    if key not in _MIN_DIMENSIONS:
        return None  # Unknown product type, skip validation
    min_w, min_h = _MIN_DIMENSIONS[key]
    if width < min_w or height < min_h:
        return (
            f"Image {width}x{height} is below minimum {min_w}x{min_h} "
            f"for product type '{key}'"
        )
    return None


# --- End copy -----------------------------------------------------------------


class TestSanitizeFilename:
    """Tests for _sanitize_filename."""

    def test_basic_concept_name(self):
        filename = _sanitize_filename("Rain Day Sticker")
        assert filename.endswith("-rain-day-sticker.png")
        # UUID prefix is 36 chars + hyphen
        assert len(filename) > 36

    def test_special_characters_removed(self):
        filename = _sanitize_filename("It's a 100% great design!!!")
        # Should strip quotes, percent, exclamation
        assert "'" not in filename
        assert "%" not in filename
        assert "!" not in filename
        assert filename.endswith(".png")

    def test_empty_name_gets_default(self):
        filename = _sanitize_filename("   ")
        assert filename.endswith("-design.png")

    def test_uuid_prefix_is_valid(self):
        filename = _sanitize_filename("test")
        uuid_part = filename[:36]
        # Should be a valid UUID4
        parsed = uuid.UUID(uuid_part)
        assert parsed.version == 4

    def test_unique_filenames(self):
        """Two calls with same name produce different filenames (different UUIDs)."""
        f1 = _sanitize_filename("same name")
        f2 = _sanitize_filename("same name")
        assert f1 != f2


class TestCheckDimensions:
    """Tests for _check_dimensions."""

    def test_sticker_meets_minimum(self):
        result = _check_dimensions(1500, 1500, "sticker")
        assert result is None

    def test_sticker_below_minimum(self):
        result = _check_dimensions(1024, 1024, "sticker")
        assert result is not None
        assert "1500x1500" in result
        assert "sticker" in result

    def test_pin_meets_minimum(self):
        result = _check_dimensions(1024, 1024, "pin")
        assert result is None

    def test_unknown_product_type_skips_check(self):
        result = _check_dimensions(100, 100, "unknown-widget")
        assert result is None

    def test_case_insensitive_product_type(self):
        result = _check_dimensions(1500, 1500, "Sticker")
        assert result is None

    def test_poster_below_minimum(self):
        result = _check_dimensions(2048, 2048, "poster")
        assert result is not None
        assert "5400x7200" in result
