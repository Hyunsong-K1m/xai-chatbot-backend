from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    APP_NAME: str = "finance-qa"
    API_PREFIX: str = "/api/v1"
    DB_URL: str = "sqlite:///./db.sqlite3"
    CHROMA_PATH: str = "./data/chroma"
    OPENAI_API_KEY: str = ""
    CORS_ORIGINS: str = "*"
    class Config: env_file = ".env"
settings = Settings()
