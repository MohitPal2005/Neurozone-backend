🚀 NeuroZone Backend (Flask + Groq + SerpAPI + Product Search Engine)

A powerful backend for the NeuroZone E-Commerce Platform, built using Flask, Groq LLM, SerpAPI Image Fetcher, and a CSV-based product search system.
Fully supports AI Chat, Product Search, Caching, Multi-Dataset Merging, and Frontend Integration.

📌 Features
🔍 1. Smart Product Search

Searches across Mobiles, Fashion, and Flipkart-style datasets

Uses RapidFuzz for fuzzy name matching

Normalizes dataset columns automatically

Returns up to 20 best results

Supports missing image auto-fetching from SerpAPI

🤖 2. AI Chat (Groq LLM)

Uses Groq’s OpenAI-compatible endpoint

Supports system prompts

Extremely fast inference

Fully compatible with React frontend

🖼 3. Image Search / Auto-Caching

If product image is missing:

Fetches from SerpAPI

Saves to /static/images/

Automatically uses cached image next time

🔐 4. CORS + Secure API Structure

CORS configured for:

localhost

production frontend (Vercel/Netlify)

Supports JSON requests safely

📁 Folder Structure
/backend
│
├── app.py                 # Main Flask server
├── config.py              # API keys (SerpAPI)
├── .env                   # GROQ API key
│
├── utils/
│   ├── product_loader.py  # Loads & cleans data
│   ├── image_search.py    # Fetch + cache images
│
├── data/
│   ├── mobiles.csv
│   ├── fashion.csv
│   ├── electronics.csv
│   
│
├── static/
│   └── images/            # Cached images
│
└── requirements.txt

🔧 Installation
1️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate    (Linux/Mac)
venv\Scripts\activate       (Windows)

2️⃣ Install dependencies
pip install -r requirements.txt

🔑 Environment Variables

Create a .env file:

GROQ_API_KEY=YOUR_GROQ_API_KEY


In config.py:

SERPAPI_KEY = "YOUR_SERPAPI_KEY"

▶️ Running the Server
python app.py


Server starts at:

http://127.0.0.1:5000

🔌 API Endpoints
🏠 Root
GET /


Returns: "NeuroZone Backend Running"

🔍 Search Products
GET /search?query=iphone 15


Response Example:

[
  {
    "model name": "iPhone 15",
    "company name": "Apple",
    "price": "79999",
    "image": "/static/images/apple_iphone_15.jpg"
  }
]

📦 Single Product
GET /product?name=poco x6

🤖 Chat AI
POST /chat


Body:

{
  "message": "Suggest a mobile under ₹20000"
}


Response:

{
  "reply": "Here are the best options under ₹20000..."
}

📩 Contact

For improvements or bugs:
Developer: Mohit Pal