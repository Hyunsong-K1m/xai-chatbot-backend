#<heo> - 환경변수 로드 설정
from pydantic import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # AI API 설정
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # 오픈뱅킹 설정
    openbanking_client_id: str = os.getenv("OPENBANKING_CLIENT_ID")
    openbanking_client_secret: str = os.getenv("OPENBANKING_CLIENT_SECRET")
    openbanking_callback_url: str = os.getenv("OPENBANKING_CALLBACK_URL")
    
    # 서버 설정
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8000"))
    debug_mode: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # CORS 설정
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # 세션 설정
    session_expire_minutes: int = int(os.getenv("SESSION_EXPIRE_MINUTES", "60"))
    max_messages_per_session: int = int(os.getenv("MAX_MESSAGES_PER_SESSION", "100"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 싱글톤 인스턴스
settings = Settings()

# 설정 검증
def validate_settings():
    """필수 설정 검증"""
    errors = []
    
    if not settings.xai_api_key and not settings.openai_api_key:
        errors.append("AI API 키가 설정되지 않았습니다 (XAI_API_KEY 또는 OPENAI_API_KEY)")
    
    if not settings.openbanking_client_id:
        errors.append("오픈뱅킹 Client ID가 설정되지 않았습니다")
    
    if not settings.openbanking_client_secret:
        errors.append("오픈뱅킹 Client Secret이 설정되지 않았습니다")
    
    if errors:
        print("⚠️ 설정 오류:")
        for error in errors:
            print(f"  - {error}")
        print("\n.env 파일을 확인해주세요!")
    else:
        print("✅ 모든 설정이 정상적으로 로드되었습니다")
    
    return len(errors) == 0