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


# --- Copied from hobson/src/hobson/tools/git_ops.py --------------------------
# Keep in sync with the source. If the validation logic changes there, update here.

_PRODUCT_TYPES = {"sticker", "mug", "pin", "print", "poster", "t-shirt"}


def _validate_product(
    slug: str,
    name: str,
    description: str,
    price: str,
    image: str,
    printful_url: str,
    product_type: str,
) -> list[str]:
    """Validate product fields before publishing."""
    errors: list[str] = []

    if not _SLUG_RE.match(slug):
        errors.append(
            f"Slug '{slug}' is not URL-safe "
            "(must match ^[a-z0-9]+(?:-[a-z0-9]+)*$)"
        )

    if not name.strip():
        errors.append("Name is empty")

    if not description.strip():
        errors.append("Description is empty")

    try:
        float(price)
    except (ValueError, TypeError):
        errors.append(f"Price '{price}' is not a valid number")

    if not image.strip():
        errors.append("Image URL is empty")

    if not printful_url.strip():
        errors.append("Printful URL is empty")

    if product_type not in _PRODUCT_TYPES:
        errors.append(
            f"Product type '{product_type}' is not valid "
            f"(must be one of: {', '.join(sorted(_PRODUCT_TYPES))})"
        )

    return errors


# --- End copy -----------------------------------------------------------------


class TestValidateProduct:
    """Tests for _validate_product pre-flight checks."""

    def test_valid_product_passes(self):
        errors = _validate_product(
            slug="suffer-smile-repeat-sticker",
            name="Suffer. Smile. Repeat. Sticker",
            description="A waterproof vinyl sticker for the trail.",
            price="14.99",
            image="https://cdn.example.com/sticker.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="sticker",
        )
        assert errors == []

    def test_invalid_slug_uppercase(self):
        errors = _validate_product(
            slug="Bad-Slug",
            name="Test Product",
            description="A description.",
            price="9.99",
            image="https://cdn.example.com/img.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="sticker",
        )
        assert len(errors) == 1
        assert "Slug" in errors[0]
        assert "URL-safe" in errors[0]

    def test_invalid_slug_special_chars(self):
        errors = _validate_product(
            slug="bad_slug!here",
            name="Test Product",
            description="A description.",
            price="9.99",
            image="https://cdn.example.com/img.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="sticker",
        )
        assert len(errors) == 1
        assert "Slug" in errors[0]

    def test_empty_name_caught(self):
        errors = _validate_product(
            slug="valid-slug",
            name="",
            description="A description.",
            price="9.99",
            image="https://cdn.example.com/img.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="sticker",
        )
        assert len(errors) == 1
        assert "Name is empty" in errors[0]

    def test_empty_description_caught(self):
        errors = _validate_product(
            slug="valid-slug",
            name="Test Product",
            description="",
            price="9.99",
            image="https://cdn.example.com/img.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="sticker",
        )
        assert len(errors) == 1
        assert "Description is empty" in errors[0]

    def test_invalid_price_not_a_number(self):
        errors = _validate_product(
            slug="valid-slug",
            name="Test Product",
            description="A description.",
            price="free",
            image="https://cdn.example.com/img.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="sticker",
        )
        assert len(errors) == 1
        assert "Price" in errors[0]
        assert "not a valid number" in errors[0]

    def test_invalid_price_empty_string(self):
        errors = _validate_product(
            slug="valid-slug",
            name="Test Product",
            description="A description.",
            price="",
            image="https://cdn.example.com/img.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="sticker",
        )
        assert len(errors) == 1
        assert "Price" in errors[0]

    def test_valid_integer_price(self):
        """Integer prices like '15' should pass."""
        errors = _validate_product(
            slug="valid-slug",
            name="Test Product",
            description="A description.",
            price="15",
            image="https://cdn.example.com/img.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="mug",
        )
        assert errors == []

    def test_empty_image_caught(self):
        errors = _validate_product(
            slug="valid-slug",
            name="Test Product",
            description="A description.",
            price="9.99",
            image="",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="sticker",
        )
        assert len(errors) == 1
        assert "Image URL is empty" in errors[0]

    def test_empty_printful_url_caught(self):
        errors = _validate_product(
            slug="valid-slug",
            name="Test Product",
            description="A description.",
            price="9.99",
            image="https://cdn.example.com/img.png",
            printful_url="",
            product_type="sticker",
        )
        assert len(errors) == 1
        assert "Printful URL is empty" in errors[0]

    def test_invalid_product_type(self):
        errors = _validate_product(
            slug="valid-slug",
            name="Test Product",
            description="A description.",
            price="9.99",
            image="https://cdn.example.com/img.png",
            printful_url="https://buildscharacter.printful.me/product/1",
            product_type="hoodie",
        )
        assert len(errors) == 1
        assert "Product type" in errors[0]
        assert "not valid" in errors[0]

    def test_all_valid_product_types(self):
        """Every allowed product_type should pass validation."""
        for ptype in ["sticker", "mug", "pin", "print", "poster", "t-shirt"]:
            errors = _validate_product(
                slug="valid-slug",
                name="Test Product",
                description="A description.",
                price="9.99",
                image="https://cdn.example.com/img.png",
                printful_url="https://buildscharacter.printful.me/product/1",
                product_type=ptype,
            )
            assert errors == [], f"product_type '{ptype}' should be valid"

    def test_multiple_errors_returned(self):
        """All failures are reported at once, not just the first."""
        errors = _validate_product(
            slug="BAD SLUG!",
            name="",
            description="",
            price="free",
            image="",
            printful_url="",
            product_type="hoodie",
        )
        assert len(errors) == 7
