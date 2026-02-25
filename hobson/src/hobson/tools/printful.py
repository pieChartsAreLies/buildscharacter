"""Printful API client for merch pipeline operations.

Uses Printful API v2 for catalog/files and v1 for store product management.
All product creation requires Telegram approval before execution.
"""

import json
import logging
import time

import boto3
import httpx
from langchain_core.tools import tool

from hobson.config import settings

logger = logging.getLogger(__name__)

_API_BASE = "https://api.printful.com"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.printful_api_key}",
        "Content-Type": "application/json",
    }


@tool
def list_catalog_products(product_type: str = "") -> str:
    """Browse Printful's catalog of available products.

    Use this to discover what products (t-shirts, stickers, mugs, hoodies, etc.)
    are available for print-on-demand. Returns product IDs needed for creating
    store products.

    Args:
        product_type: Optional filter by type (e.g., 'T-SHIRT', 'STICKER',
                      'MUG', 'POSTER'). Leave empty to browse all.
    """
    params = {"limit": 20}
    if product_type:
        params["type"] = product_type.upper()

    with httpx.Client(headers=_headers(), timeout=30) as client:
        resp = client.get(f"{_API_BASE}/v2/catalog-products", params=params)
        resp.raise_for_status()
        data = resp.json().get("data", [])

    if not data:
        return f"No catalog products found for type '{product_type}'."

    lines = []
    for p in data:
        lines.append(
            f"- ID {p['id']}: {p['name']} "
            f"(type: {p.get('type', '?')}, variants: {p.get('variant_count', '?')})"
        )
    return f"Found {len(data)} products:\n" + "\n".join(lines)


@tool
def get_catalog_product_variants(catalog_product_id: int) -> str:
    """Get available variants (sizes, colors) for a specific catalog product.

    Use this after finding a product via list_catalog_products to see what
    sizes and colors are available before creating a store product.

    Args:
        catalog_product_id: The Printful catalog product ID (e.g., 358 for a sticker).
    """
    with httpx.Client(headers=_headers(), timeout=30) as client:
        resp = client.get(
            f"{_API_BASE}/v2/catalog-products/{catalog_product_id}/catalog-variants"
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])

    if not data:
        return f"No variants found for product {catalog_product_id}."

    lines = []
    for v in data[:30]:  # Cap output to avoid token bloat
        color = v.get("color", "")
        size = v.get("size", "")
        price = v.get("price", "?")
        lines.append(
            f"- Variant {v['id']}: {size} / {color} (${price})"
        )

    total = len(data)
    shown = min(total, 30)
    return f"Showing {shown}/{total} variants for product {catalog_product_id}:\n" + "\n".join(lines)


@tool
def upload_design_file(image_url: str, filename: str) -> str:
    """Upload a design image to Printful's file library.

    The image must be accessible via URL. Printful will download and process it.
    For print-on-demand, images should be high resolution (300+ DPI recommended).

    Args:
        image_url: Public URL of the image to upload.
        filename: Desired filename (e.g., 'rain-day-3-sticker.png').
    """
    payload = {
        "role": "printfile",
        "url": image_url,
        "filename": filename,
        "visible": True,
    }

    with httpx.Client(headers=_headers(), timeout=60) as client:
        resp = client.post(f"{_API_BASE}/v2/files", json=payload)
        resp.raise_for_status()
        data = resp.json().get("data", {})

    file_id = data.get("id", "?")
    status = data.get("status", "?")
    dims = f"{data.get('width', '?')}x{data.get('height', '?')}"
    dpi = data.get("dpi", "?")
    preview = data.get("preview_url", "")

    return (
        f"File uploaded: ID {file_id}, status: {status}, "
        f"dimensions: {dims}, DPI: {dpi}\n"
        f"Preview: {preview}"
    )


@tool
def create_store_product(
    name: str,
    catalog_variant_id: int,
    design_file_url: str,
    description: str = "",
    retail_price: str = "",
) -> str:
    """Create a new product in the Printful store with a design applied.

    IMPORTANT: Always request Telegram approval before calling this, as it
    creates a product that will be visible in the store.

    This creates a draft order-style product. The design image is applied to
    the front placement using DTG (direct-to-garment) printing.

    Args:
        name: Product name (e.g., 'Rain on Day 3 - Sticker').
        catalog_variant_id: Printful variant ID from get_catalog_product_variants.
        design_file_url: URL of the uploaded design file (from upload_design_file).
        description: Optional product description.
        retail_price: Optional retail price (e.g., '12.99'). Omit for Printful default.
    """
    # Use v1 sync product creation (more straightforward for store products)
    sync_product = {
        "name": name,
    }
    if description:
        sync_product["description"] = description

    sync_variant = {
        "variant_id": catalog_variant_id,
        "files": [
            {
                "type": "default",
                "url": design_file_url,
            }
        ],
    }
    if retail_price:
        sync_variant["retail_price"] = retail_price

    payload = {
        "sync_product": sync_product,
        "sync_variants": [sync_variant],
    }

    with httpx.Client(headers=_headers(), timeout=60) as client:
        resp = client.post(f"{_API_BASE}/store/products", json=payload)
        resp.raise_for_status()
        result = resp.json().get("result", {})

    product_id = result.get("sync_product", {}).get("id", "?")
    return f"Store product created: ID {product_id}, name: '{name}'"


@tool
def list_store_products() -> str:
    """List all products currently in the Printful store.

    Returns product names, IDs, sync status, and variant counts.
    Use this to check what's already published and avoid duplicates.
    """
    with httpx.Client(headers=_headers(), timeout=30) as client:
        resp = client.get(
            f"{_API_BASE}/store/products",
            params={"limit": 50},
        )
        resp.raise_for_status()
        result = resp.json().get("result", [])

    if not result:
        return "No products in the store yet."

    lines = []
    for p in result:
        sync_product = p.get("sync_product", p)
        name = sync_product.get("name", "?")
        pid = sync_product.get("id", "?")
        variants = sync_product.get("variants", 0)
        status = sync_product.get("synced", False)
        lines.append(
            f"- ID {pid}: {name} (variants: {variants}, synced: {status})"
        )

    return f"{len(result)} store products:\n" + "\n".join(lines)


@tool
def get_mockup_styles(catalog_product_id: int) -> str:
    """Get available mockup styles for a catalog product.

    Returns style IDs and names that can be used with generate_product_mockup.
    Prioritizes default mockup styles.

    Args:
        catalog_product_id: The Printful catalog product ID.
    """
    with httpx.Client(headers=_headers(), timeout=30) as client:
        resp = client.get(
            f"{_API_BASE}/v2/catalog-products/{catalog_product_id}/mockup-styles",
            params={"default_mockup_styles": "true", "limit": 20},
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])

    if not data:
        return f"No mockup styles found for product {catalog_product_id}."

    lines = []
    for placement in data:
        placement_name = placement.get("placement", "?")
        for style in placement.get("mockup_styles", []):
            lines.append(
                f"- Style {style['id']}: {style.get('view_name', '?')} "
                f"(category: {style.get('category_name', '?')}, "
                f"placement: {placement_name})"
            )

    return f"Found {len(lines)} mockup styles for product {catalog_product_id}:\n" + "\n".join(lines)


def _upload_mockup_to_r2(image_bytes: bytes, concept_name: str) -> str:
    """Upload mockup image bytes to R2 and return public URL."""
    import re as _re
    import uuid as _uuid

    sanitized = _re.sub(r"[^a-z0-9-]", "-", concept_name.lower().strip())
    sanitized = _re.sub(r"-+", "-", sanitized).strip("-") or "mockup"
    filename = f"{_uuid.uuid4()}-{sanitized}-mockup.jpg"
    r2_key = f"mockups/{filename}"

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
        ContentType="image/jpeg",
    )

    return f"{settings.r2_public_url}/{r2_key}"


_MOCKUP_POLL_INTERVAL = 5  # seconds
_MOCKUP_POLL_TIMEOUT = 120  # seconds


@tool
def generate_product_mockup(
    catalog_product_id: int,
    catalog_variant_id: int,
    design_image_url: str,
    concept_name: str = "product",
) -> str:
    """Generate a realistic product mockup image via Printful's Mockup Generator.

    Creates a mockup showing the design on the actual product (e.g., sticker on
    a surface, mug on a desk). The mockup image is uploaded to R2 for permanent
    storage since Printful's generated URLs are temporary.

    On failure or timeout, falls back to the raw design image URL.

    Args:
        catalog_product_id: Printful catalog product ID.
        catalog_variant_id: Printful catalog variant ID.
        design_image_url: Public URL of the design image (from R2).
        concept_name: Human-readable name for the concept (used in filenames).
    """
    headers = _headers()

    # Step 1: Get default mockup style
    try:
        with httpx.Client(headers=headers, timeout=30) as client:
            resp = client.get(
                f"{_API_BASE}/v2/catalog-products/{catalog_product_id}/mockup-styles",
                params={"default_mockup_styles": "true", "limit": 5},
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
    except Exception as e:
        logger.warning("Failed to fetch mockup styles: %s. Falling back to design URL.", e)
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": f"Mockup styles fetch failed: {e}",
        })

    if not data or not data[0].get("mockup_styles"):
        logger.warning("No mockup styles available for product %d", catalog_product_id)
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": "No mockup styles available",
        })

    # Pick first default style
    placement_info = data[0]
    style = placement_info["mockup_styles"][0]
    style_id = style["id"]
    placement = placement_info.get("placement", "front")

    # Step 2: Create mockup task
    payload = {
        "format": "jpg",
        "products": [
            {
                "source": "catalog",
                "mockup_style_ids": [style_id],
                "catalog_product_id": catalog_product_id,
                "catalog_variant_ids": [catalog_variant_id],
                "placements": [
                    {
                        "placement": placement,
                        "technique": placement_info.get("technique", "dtg"),
                        "layers": [
                            {
                                "type": "file",
                                "url": design_image_url,
                            }
                        ],
                    }
                ],
            }
        ],
    }

    try:
        with httpx.Client(headers=headers, timeout=30) as client:
            resp = client.post(f"{_API_BASE}/v2/mockup-generator", json=payload)
            resp.raise_for_status()
            task_data = resp.json().get("data", [])
    except Exception as e:
        logger.warning("Mockup task creation failed: %s. Falling back.", e)
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": f"Mockup task creation failed: {e}",
        })

    if not task_data:
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": "No task data returned from mockup generator",
        })

    task_id = task_data[0].get("id") if isinstance(task_data, list) else task_data.get("id")
    if not task_id:
        task_id = task_data.get("task_id") if isinstance(task_data, dict) else None
    if not task_id:
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": "Could not extract task ID from mockup response",
        })

    # Step 3: Poll for completion
    elapsed = 0
    mockup_url = None
    while elapsed < _MOCKUP_POLL_TIMEOUT:
        time.sleep(_MOCKUP_POLL_INTERVAL)
        elapsed += _MOCKUP_POLL_INTERVAL

        try:
            with httpx.Client(headers=headers, timeout=30) as client:
                resp = client.get(
                    f"{_API_BASE}/v2/mockup-tasks",
                    params={"id": str(task_id)},
                )
                resp.raise_for_status()
                tasks = resp.json().get("data", [])
        except Exception as e:
            logger.warning("Mockup poll failed at %ds: %s", elapsed, e)
            continue

        if not tasks:
            continue

        task = tasks[0]
        status = task.get("status", "")

        if status == "completed":
            variant_mockups = task.get("catalog_variant_mockups", [])
            if variant_mockups:
                mockups = variant_mockups[0].get("mockups", [])
                if mockups:
                    mockup_url = mockups[0].get("mockup_url")
            break
        elif status == "failed":
            reasons = task.get("failure_reasons", [])
            reason_str = "; ".join(r.get("detail", "unknown") for r in reasons)
            logger.warning("Mockup task %s failed: %s", task_id, reason_str)
            return json.dumps({
                "status": "fallback",
                "image_url": design_image_url,
                "reason": f"Mockup generation failed: {reason_str}",
            })

    if not mockup_url:
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": f"Mockup poll timed out after {_MOCKUP_POLL_TIMEOUT}s",
        })

    # Step 4: Download mockup and re-upload to R2 (Printful URLs are temporary)
    try:
        with httpx.Client(timeout=30) as client:
            img_resp = client.get(mockup_url)
            img_resp.raise_for_status()
            mockup_bytes = img_resp.content

        r2_url = _upload_mockup_to_r2(mockup_bytes, concept_name)
    except Exception as e:
        logger.warning("Mockup download/upload failed: %s. Using Printful URL.", e)
        r2_url = mockup_url  # Use temporary URL as last resort

    return json.dumps({
        "status": "success",
        "image_url": r2_url,
        "mockup_style_id": style_id,
        "task_id": task_id,
    })
