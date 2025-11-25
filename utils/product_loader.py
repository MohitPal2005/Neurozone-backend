import os
import pandas as pd
from rapidfuzz import fuzz
from .image_search import clean_columns

DATA_DIR = "data"


def load_mobile_data():
    path = os.path.join(DATA_DIR, "mobiles.csv")
    print(f"[LOAD] Mobiles: {path}")

    try:
        df = pd.read_csv(path, encoding="utf-8")
    except Exception:
        df = pd.read_csv(path, encoding="latin1")

    df.columns = df.columns.str.lower().str.strip()
    df.fillna("", inplace=True)

    df["category"] = "Mobiles"

    if "model name" not in df.columns:
        df.rename(columns={"model": "model name"}, inplace=True)

    # brand → company name
    if "company name" not in df.columns:
        if "company" in df.columns:
            df.rename(columns={"company": "company name"}, inplace=True)
        elif "brand" in df.columns:
            df.rename(columns={"brand": "company name"}, inplace=True)

    return df



def load_electronics_data():
    path = os.path.join(DATA_DIR, "electronics.csv")
    print(f"[LOAD] Electronics: {path}")

    df = pd.read_csv(path, on_bad_lines="skip")
    df.columns = df.columns.str.lower().str.strip()
    df.fillna("", inplace=True)

    df.rename(
        columns={
            "product_name": "model name",
            "brand": "company name",
            "price": "price",
        },
        inplace=True,
    )

    df["category"] = "Electronics"
    return df


def load_fashion_data():
    path = os.path.join(DATA_DIR, "fashion.csv")
    print(f"[LOAD] Fashion: {path}")

    df = pd.read_csv(path, on_bad_lines="skip")
    df.columns = df.columns.str.lower().str.strip()
    df.fillna("", inplace=True)

    df.rename(
        columns={
            "name": "model name",
            "brand": "company name",
            "price": "price",
        },
        inplace=True,
    )

    df["category"] = "Fashion"
    return df



def compute_score(query, row):
    """
    Hybrid scoring:
    1) Exact token match
    2) Fuzzy brand match
    3) Fuzzy model match
    """
    query = str(query).lower()
    brand = str(row.get("company name", "")).lower()
    name = str(row.get("model name", "")).lower()
    category = str(row.get("category", "")).lower()

    full_str = f"{brand} {name} {category}"

    # Token Score (strict)
    token_score = sum(1 for token in query.split() if token in full_str)

    # Fuzzy Scores
    brand_score = fuzz.partial_ratio(query, brand)
    model_score = fuzz.partial_ratio(query, name)
    overall = fuzz.token_sort_ratio(query, full_str)

    # Weighted hybrid score
    final_score = (
        token_score * 40
        + brand_score * 0.3
        + model_score * 0.3
        + overall * 0.4
    )
    return final_score



def search_products(query, detailed: bool = False):
    """
    Search products across all categories.

    - detailed=False → for /search results (FAST, 1 main image)
    - detailed=True  → for /product details (adds image gallery)
    """
    mob = load_mobile_data()
    elec = load_electronics_data()
    fashion = load_fashion_data()

    df = pd.concat([mob, elec, fashion], ignore_index=True)
    results = []

    for _, row in df.iterrows():
        score = compute_score(query, row)
        if score >= 35:
            results.append((score, row))

    # Sort by descending score
    results.sort(key=lambda x: x[0], reverse=True)

    # Convert rows → frontend format
    return [clean_columns(row, detailed=detailed) for score, row in results[:20]]
