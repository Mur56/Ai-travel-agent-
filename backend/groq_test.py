from dotenv import load_dotenv
from utils.model_loader import ModelLoader


load_dotenv()

loader = ModelLoader(model_provider="openai")
llm = loader.load_llm()

response = llm.invoke("Reply only with: OK")

if response.content.strip() != "OK":
    raise RuntimeError("❌ Groq responded incorrectly")

print("✅ Groq health check PASSED")
