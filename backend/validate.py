import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")

if not key:
    raise RuntimeError("❌ GROQ_API_KEY not found")

if key.startswith(("'", '"')) or key.endswith(("'", '"')):
    raise RuntimeError("❌ GROQ_API_KEY contains quotes — remove them")

if len(key) < 30:
    raise RuntimeError("❌ GROQ_API_KEY looks too short")

print("✅ GROQ_API_KEY is valid")
print("Key length:", len(key))
