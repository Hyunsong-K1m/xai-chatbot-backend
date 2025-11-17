from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "finance-qa"
    API_PREFIX: str = "/api/v1"
    DB_URL: str = "sqlite:///./db.sqlite3"
    CHROMA_PATH: str = "./data/chroma"
    OPENAI_API_KEY: str = ""
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()

JSON_PATH = "/home/xai/fastapi-backend/data/json"
PERSIST_DIRECTORY = "/home/xai/fastapi-backend/data/chroma"
COLLECTION_NAME = "financial_products"   
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "nlpai-lab/KURE-v1"
MODEL_KWARGS = {"device": "cpu"}
ENCODE_KWARGS = {"normalize_embeddings": True}
SEARCH_K = 3
