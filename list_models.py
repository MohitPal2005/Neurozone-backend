import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()  # Load your .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# List all available models
models = genai.list_models()
for m in models:
    print(m.name, "-", getattr(m, "description", ""))
