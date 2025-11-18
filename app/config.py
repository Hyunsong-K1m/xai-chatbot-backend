from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

# 프로젝트 루트 디렉토리 (config.py 기준)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "finance-qa"
    API_PREFIX: str = "/api/v1"
    DB_URL: str = "sqlite:///./db.sqlite3"
    CHROMA_PATH: str = str(BASE_DIR / "data" / "chroma")
    OPENAI_API_KEY: str = ""
    CORS_ORIGINS: str = "*"

    # OpenBanking 설정
    OPENBANKING_CLIENT_ID: str = ""
    OPENBANKING_CLIENT_SECRET: str = ""
    OPENBANKING_CALLBACK_URL: str = ""

    # 서버 설정
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG_MODE: bool = True
    ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        extra = "ignore"  # 추가 필드 허용

settings = Settings()

# 경로 설정 (Windows/Linux 모두 호환)
JSON_PATH = str(BASE_DIR / "data" / "json")
PERSIST_DIRECTORY = str(BASE_DIR / "data" / "chroma")
COLLECTION_NAME = "financial_products"

# AI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 임베딩 모델 설정
MODEL_NAME = "nlpai-lab/KURE-v1"
MODEL_KWARGS = {"device": "cpu"}
ENCODE_KWARGS = {"normalize_embeddings": True}
SEARCH_K = 3
