# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Project Info ---
    PROJECT_NAME: str = "Tour Planner AI"
    VERSION: str = "1.0.0"

    # --- AI & Database Keys ---
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    PINECONE_INDEX: str = "tour-planner-vector-store"

    # --- Redis Config ---
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_MAX_MESSAGES: int = 20

    # --- Business Logic (The "Editable" part) ---
    ALLOWED_CITIES: list = ["kathmandu", "pokhara", "chitwan", "lumbini", "nagarkot"]

    # --- Pinecone Config ---
    PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", 768))


# Global instance
settings = Settings()
