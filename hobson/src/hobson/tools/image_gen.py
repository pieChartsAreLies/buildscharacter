"""Image generation and R2 upload tools for design batch workflow."""

import base64
import io
import json
import logging
import re
import time
import uuid

import boto3
from google import genai
from google.api_core import exceptions as google_exceptions
from google.genai import types
from langchain_core.tools import tool
from PIL import Image

from hobson.config import settings
from hobson.db import HobsonDB

logger = logging.getLogger(__name__)

_SANITIZE_RE = re.compile(r"[^a-z0-9-]")

# Minimum pixel dimensions per product type (from Printful specs)
_MIN_DIMENSIONS = {
    "sticker": (1500, 1500),
    "pin": (1000, 1000),
    "small-print": (2400, 3000),
    "poster": (5400, 7200),
    "t-shirt": (4500, 5100),
}

_MODEL = "imagen-4.0-generate-001"
_MAX_RETRIES = 3

# Module-level DB instance (reused across tool calls)
_db = HobsonDB(settings.database_url)


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
        return None
    min_w, min_h = _MIN_DIMENSIONS[key]
    if width < min_w or height < min_h:
        return (
            f"Image {width}x{height} is below minimum {min_w}x{min_h} "
            f"for product type '{key}'"
        )
    return None


def _rank_images_with_vision(
    images: list[bytes], prompt: str
) -> int:
    """Use Gemini Flash to rank candidate images and return index of the best one.

    Falls back to index 0 if the vision call fails.
    """
    if len(images) <= 1:
        return 0

    try:
        client = genai.Client(api_key=settings.google_api_key)
        contents = [
            f"You are evaluating {len(images)} candidate images generated from this prompt:\n\n"
            f"\"{prompt}\"\n\n"
            "Rank them by: brand alignment (outdoor/endurance humor), visual clarity, "
            "print-readiness (clean lines, no artifacts), and overall quality.\n\n"
            "Reply with ONLY the number (1-based) of the best image. Nothing else."
        ]
        for i, img_bytes in enumerate(images):
            contents.append(f"\nImage {i + 1}:")
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )
        # Robust parsing: extract first number from response
        match = re.search(r"\d+", response.text)
        if not match:
            logger.warning("Vision ranker returned no number: %r, using 0", response.text)
            return 0
        choice = int(match.group()) - 1  # Convert 1-based to 0-based
        if 0 <= choice < len(images):
            return choice
        logger.warning("Vision ranker returned out-of-range index %d, using 0", choice)
        return 0
    except (ValueError, AttributeError) as e:
        logger.warning("Vision ranking parse error (%s), using first image", e)
        return 0
    except Exception as e:
        logger.warning("Vision ranking API error (%s), using first image", e)
        return 0


@tool
async def generate_design_image(
    prompt: str,
    concept_name: str,
    product_type: str = "sticker",
    aspect_ratio: str = "1:1",
) -> str:
    """Generate a design image using Gemini Imagen 4.0.

    Generates 4 candidate images, uses vision AI to select the best one,
    and validates dimensions against product requirements. Returns a JSON
    string with generation_id and image_base64 for use with upload_to_r2.

    Args:
        prompt: Detailed image generation prompt assembled from the structured template.
        concept_name: Human-readable concept name (for logging and filenames).
        product_type: Target product type for dimension validation (sticker, pin, poster, etc.).
        aspect_ratio: Image aspect ratio. One of "1:1", "3:4", "4:3", "9:16", "16:9".
    """
    # Retry loop for transient API failures
    last_error = None
    for attempt in range(_MAX_RETRIES):
        try:
            client = genai.Client(api_key=settings.google_api_key)
            response = client.models.generate_images(
                model=_MODEL,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=4,
                    aspect_ratio=aspect_ratio,
                    include_rai_reason=True,
                    output_mime_type="image/png",
                ),
            )
            break
        except (
            google_exceptions.ServiceUnavailable,
            google_exceptions.TooManyRequests,
            google_exceptions.InternalServerError,
            ConnectionError,
            TimeoutError,
        ) as e:
            last_error = e
            if attempt < _MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning(
                    "Imagen API attempt %d failed (%s), retrying in %ds",
                    attempt + 1, e, wait,
                )
                time.sleep(wait)
            continue
        except (
            google_exceptions.InvalidArgument,
            google_exceptions.PermissionDenied,
            google_exceptions.NotFound,
        ) as e:
            # Non-retryable errors: bad request, auth failure, wrong model
            _db.log_design_generation(
                concept_name=concept_name,
                generation_prompt=prompt,
                model_version=_MODEL,
                product_type=product_type,
                generation_status="failed",
                status_reason=f"Non-retryable API error: {e}",
            )
            return json.dumps({
                "status": "error",
                "message": f"Image generation failed (non-retryable): {e}",
            })
    else:
        # All retries exhausted
        _db.log_design_generation(
            concept_name=concept_name,
            generation_prompt=prompt,
            model_version=_MODEL,
            product_type=product_type,
            generation_status="failed",
            status_reason=f"API error after {_MAX_RETRIES} retries: {last_error}",
        )
        return json.dumps({
            "status": "error",
            "message": f"Image generation failed after {_MAX_RETRIES} retries: {last_error}",
        })

    # Check for safety-filtered or empty response
    if not response.generated_images:
        reason = "No images returned (likely safety filter)"
        _db.log_design_generation(
            concept_name=concept_name,
            generation_prompt=prompt,
            model_version=_MODEL,
            product_type=product_type,
            generation_status="filtered",
            status_reason=reason,
        )
        return json.dumps({
            "status": "filtered",
            "message": f"{reason}. Try modifying the prompt to avoid content filter triggers.",
        })

    # Collect raw bytes from all candidates
    candidate_bytes = []
    for gi in response.generated_images:
        img_data = gi.image.image_bytes
        if isinstance(img_data, str):
            img_data = base64.b64decode(img_data)
        candidate_bytes.append(img_data)

    # Rank with vision model and select best
    best_idx = _rank_images_with_vision(candidate_bytes, prompt)
    selected_bytes = candidate_bytes[best_idx]

    # Check dimensions
    img = Image.open(io.BytesIO(selected_bytes))
    width, height = img.size
    dim_warning = _check_dimensions(width, height, product_type)
    if dim_warning:
        logger.warning(dim_warning)

    # Encode as base64 for return
    image_b64 = base64.b64encode(selected_bytes).decode("utf-8")

    # Log to DB and get the generation_id for targeted upload_to_r2 update
    generation_id = _db.log_design_generation(
        concept_name=concept_name,
        generation_prompt=prompt,
        model_version=_MODEL,
        product_type=product_type,
        generation_status="success",
        image_width=width,
        image_height=height,
    )

    result = {
        "status": "success",
        "generation_id": generation_id,
        "concept_name": concept_name,
        "width": width,
        "height": height,
        "candidates": len(candidate_bytes),
        "selected": best_idx + 1,
        "model": _MODEL,
        "image_base64": image_b64,
    }
    if dim_warning:
        result["dimension_warning"] = dim_warning

    return json.dumps(result)


@tool
async def upload_to_r2(
    image_base64: str,
    concept_name: str,
    generation_id: int = 0,
) -> str:
    """Upload a generated design image to Cloudflare R2 and return its public URL.

    Args:
        image_base64: Base64-encoded PNG image bytes (from generate_design_image output, the image_base64 field).
        concept_name: Human-readable concept name (used in filename after UUID prefix).
        generation_id: Database row ID from generate_design_image output (for tracking). Pass 0 if unknown.
    """
    image_bytes = base64.b64decode(image_base64)
    filename = _sanitize_filename(concept_name)
    r2_key = f"designs/{filename}"

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

    s3.put_object(
        Bucket=settings.r2_bucket_name,
        Key=r2_key,
        Body=image_bytes,
        ContentType="image/png",
    )

    public_url = f"{settings.r2_public_url}/{r2_key}"

    # Update the specific design_generations record with the URL (targeted by ID)
    if generation_id:
        try:
            with _db._conn() as conn:
                conn.execute(
                    """UPDATE hobson.design_generations
                       SET image_url = %s, r2_filename = %s
                       WHERE id = %s""",
                    (public_url, filename, generation_id),
                )
        except Exception as e:
            logger.warning("Failed to update design_generations id=%d: %s", generation_id, e)

    return json.dumps({
        "status": "success",
        "url": public_url,
        "filename": filename,
        "generation_id": generation_id,
    })
