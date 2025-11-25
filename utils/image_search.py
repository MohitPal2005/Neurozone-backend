import os
import re
import requests
import serpapi
from config import SERPAPI_KEY


STATIC_DIR = os.path.join("static", "images")
os.makedirs(STATIC_DIR, exist_ok=True)


def _slug(query: str) -> str:
    """Make a safe prefix for filenames from query."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", str(query).lower())


def fetch_image_urls(query: str, max_images: int = 3):
    """
    Return up to `max_images` local image paths for a product.

    - First, check already-downloaded images in static/images.
    - If enough images exist → NO SerpAPI call.
    - Otherwise, call SerpAPI ONCE and fill remaining slots.
    """
    if not query:
        return ["/static/images/default.jpg"]

    safe_prefix = _slug(query)
    local_paths = []

    for idx in range(max_images):
        fname = f"{safe_prefix}_{idx}.jpg"
        fpath = os.path.join(STATIC_DIR, fname)
        if os.path.exists(fpath):
            local_paths.append(f"/static/images/{fname}")
        else:
            break  


    if len(local_paths) >= max_images:
        return local_paths[:max_images]

    try:
        client = serpapi.Client(api_key=SERPAPI_KEY)
        results = client.search(q=query, tbm="isch", ijn="0")
        images = results.get("images_results", [])


        start_idx = len(local_paths)
        needed = max_images - len(local_paths)

        count_downloaded = 0
        for i in range(start_idx, start_idx + needed):
            if i >= len(images):
                break

            url = images[i].get("original", "")
            if not url:
                continue

            fname = f"{safe_prefix}_{i}.jpg"
            fpath = os.path.join(STATIC_DIR, fname)

            
            if os.path.exists(fpath):
                local_paths.append(f"/static/images/{fname}")
                count_downloaded += 1
                continue

            try:
                img_data = requests.get(url, timeout=5).content
                with open(fpath, "wb") as f:
                    f.write(img_data)
                local_paths.append(f"/static/images/{fname}")
                count_downloaded += 1
            except Exception:
                continue

       
        if not local_paths:
            return ["/static/images/default.jpg"]

        return local_paths[:max_images]

    except Exception:
        return local_paths or ["/static/images/default.jpg"]


def fetch_image_url(query: str) -> str:
    """
    Convenience helper: return a SINGLE main image.
    Uses the same caching logic as fetch_image_urls.
    """
    return fetch_image_urls(query, max_images=1)[0]


def clean_columns(row, detailed: bool = False):
    """
    Convert a raw pandas row into a clean dict for the frontend.

    - When detailed=False  → used for SEARCH results (fast).
    - When detailed=True   → used for PRODUCT DETAILS (add gallery images).
    """
    cat = row.get("category", "")
    model = row.get("model name", "")
    brand = row.get("company name", "")
    query = f"{brand} {model}".strip()

    base = {
        "model name": model,
        "company name": brand,
        "category": cat,
    }

    if cat == "Mobiles":
        main_image = fetch_image_url(query)

        images = [main_image]
        if detailed:
            gallery = fetch_image_urls(query, max_images=2)
            uniq = []
            for img in gallery:
                if img not in uniq:
                    uniq.append(img)
            images = uniq

        base.update(
            {
                "price": row.get("launched price (india)", ""),
                "ram": row.get("ram", ""),
                "processor": row.get("processor", ""),
                "battery capacity": row.get("battery capacity", ""),
                "screen size": row.get("screen size", ""),
                "image": images[0],
                "images": images,
            }
        )
        return base

    if cat == "Electronics":
        csv_image = row.get("image", "")
        main_image = csv_image or fetch_image_url(query)

        images = [main_image]
        if detailed:
            gallery = fetch_image_urls(query, max_images=3)
            extra = [img for img in gallery if img != main_image]
            images = [main_image] + extra[:2]

        base.update(
            {
                "price": row.get("price", ""),
                "description": row.get("description", ""),
                "image": images[0],
                "images": images,
            }
        )
        return base

    if cat == "Fashion":
        csv_image = row.get("image", "")
        main_image = csv_image or fetch_image_url(query)

        images = [main_image]
        if detailed:
            gallery = fetch_image_urls(query, max_images=3)
            extra = [img for img in gallery if img != main_image]
            images = [main_image] + extra[:2]

        base.update(
            {
                "price": row.get("price", ""),
                "image": images[0],
                "images": images,
            }
        )
        return base

    main_image = row.get("image", "") or fetch_image_url(query)
    images = [main_image]
    if detailed:
        gallery = fetch_image_urls(query, max_images=3)
        extra = [img for img in gallery if img != main_image]
        images = [main_image] + extra[:2]

    base.update(
        {
            "price": row.get("price", ""),
            "image": images[0],
            "images": images,
        }
    )
    return base
