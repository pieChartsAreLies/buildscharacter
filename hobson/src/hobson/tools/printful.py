"""Printful API client for merch pipeline operations.

Uses Printful API v2 for catalog/files and v1 for store product management.
All product creation requires Telegram approval before execution.
"""

import httpx
from langchain_core.tools import tool

from hobson.config import settings

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
