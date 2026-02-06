import os
from dotenv import load_dotenv
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()  # ✅ ensure env variables are loaded


class ConfigLoader:
    def __init__(self):
        print("Loaded config.....")
        self.config = load_config()
    
    def __getitem__(self, key):
        return self.config[key]


class ModelLoader(BaseModel):
    model_provider: Literal["groq", "openai", "google"] = "google"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        self.config = ConfigLoader()
    
    class Config:
        arbitrary_types_allowed = True
    
    def load_llm(self):
        """
        Load and return the LLM model.
        """
        print("LLM loading...")
        print(f"Loading model from provider: {self.model_provider}")

        # ===================== GROQ =====================
        if self.model_provider == "groq":
            print("Loading LLM from Groq..............")

            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise RuntimeError("GROQ_API_KEY is missing")

            model_name = self.config["llm"]["groq"]["model_name"]
            if not model_name:
                raise RuntimeError("Groq model_name missing in config")

            llm = ChatGroq(
                model=model_name,
                api_key=groq_api_key,
                timeout=30
            )

            print("✅ Groq LLM loaded")
            return llm

        # ===================== OPENAI =====================
        elif self.model_provider == "openai":
            print("Loading LLM from OpenAI..............")

            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is missing")

            model_name = self.config["llm"]["openai"]["model_name"]
            if not model_name:
                raise RuntimeError("OpenAI model_name missing in config")

            llm = ChatOpenAI(
                model=model_name,   # ✅ FIXED (no hardcoding)
                api_key=openai_api_key,
                timeout=30
            )

            print("✅ OpenAI LLM loaded")
            return llm

        # ===================== GOOGLE GEMINI =====================
        elif self.model_provider == "google":
            print("Loading LLM from Google Gemini.............")

            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                raise RuntimeError("GOOGLE_API_KEY is missing")

            model_name = self.config["llm"]["google"]["model_name"]
            if not model_name:
                raise RuntimeError("Google model_name missing in config")

            llm = ChatGoogleGenerativeAI(
                model=model_name,
                api_key=google_api_key,
                timeout=30
            )

            print("✅ Google Gemini LLM loaded")
            return llm

        # ===================== INVALID =====================
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
