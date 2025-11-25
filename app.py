from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import logging

from utils.product_loader import search_products
from utils.image_search import fetch_image_url


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
if not GROQ_API_KEY:
    logging.warning(
        "GROQ_API_KEY not found in .env — chat endpoint will fail until you set it."
    )

GROQ_OPENAI_BASE = "https://api.groq.com/openai/v1"  # OpenAI-compatible base


app = Flask(__name__)
CORS(
    app,
    origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-frontend.vercel.app",
    ],
)

os.makedirs("static/images", exist_ok=True)



def call_groq_chat(
    user_message: str,
    system_prompt: str = None,
    model: str = "openai/gpt-oss-20b",
    temperature: float = 0.2,
    max_tokens: int = 512,
    timeout: int = 30,
):
    """
    Call the Groq OpenAI-compatible chat completions endpoint and return assistant text.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured on server.")

    url = f"{GROQ_OPENAI_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"Groq API error {resp.status_code}: {resp.text}") from e

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Unexpected Groq response shape: {data}") from e



@app.route("/")
def home():
    return "NeuroZone Backend Running"


@app.route("/product", methods=["GET"])
def get_product():
    """
    Full product details + image gallery (used on ProductDetails page).
    """
    name = request.args.get("name", "")
    if not name:
        return jsonify({"error": "Missing product name"}), 400

    # detailed=True → adds images[ ] gallery
    results = search_products(name, detailed=True)
    return jsonify(results[0] if results else {"error": "Product not found"})


@app.route("/search", methods=["GET"])
def search():
    """
    Fast search endpoint used by SearchResults page.
    Returns light objects with 1 main image per product.
    """
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    
    results = search_products(query, detailed=False)

    for product in results:
        if not product.get("image"):
            fetched = fetch_image_url(
                product.get("company name", "") + " " + product.get("model name", "")
            )
            product["image"] = fetched if fetched else "/static/images/default.jpg"

    return jsonify(results)


@app.route("/chat", methods=["POST"])
def chat():
    """
    POST JSON: { "message": "text", optional "system": "context", optional "model": "..." }
    Returns: { "reply": "assistant text" }
    """
    body = request.json or {}
    user_message = body.get("message", "")
    system_prompt = body.get("system")
    model = body.get("model", "openai/gpt-oss-20b")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        assistant_text = call_groq_chat(
            user_message=user_message,
            system_prompt=system_prompt,
            model=model,
            temperature=0.2,
            max_tokens=512,
        )
        return jsonify({"reply": assistant_text})
    except Exception as e:
        logging.exception("Chat error")
        return jsonify({"error": str(e)}), 500


@app.route("/list-models", methods=["GET"])
def list_models():
    """
    Debug endpoint to list models available via the Groq OpenAI-compatible route.
    """
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY not configured"}), 500
    url = f"{GROQ_OPENAI_BASE}/models"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        logging.exception("list-models failed")
        return jsonify({"error": str(e), "body": getattr(e, "response", None)}), 500



if __name__ == "__main__":
    app.run(debug=True)
