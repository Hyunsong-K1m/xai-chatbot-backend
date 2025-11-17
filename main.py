from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 설정 import (config.py가 있는 경우)
try:
    from app.core.config import settings, validate_settings
    USE_CONFIG = True
except ImportError:
    print("⚠️ config.py를 찾을 수 없습니다. 기본 설정을 사용합니다.")
    USE_CONFIG = False
    
    # 기본 설정 (config.py가 없을 때)
    class Settings:
        server_host = os.getenv("SERVER_HOST", "0.0.0.0")
        server_port = int(os.getenv("SERVER_PORT", "8000"))
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    settings = Settings()
    
    def validate_settings():
        # 최소한의 검증
        if not os.getenv("XAI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("⚠️ 경고: AI API 키가 설정되지 않았습니다.")
            print("  .env 파일에 XAI_API_KEY 또는 OPENAI_API_KEY를 설정하세요.")
            return True  # 경고만 하고 서버는 실행
        return True

app = FastAPI(
    title="XAI Chatbot API",
    description="XAI Chatbot Backend with Mobile API Support",
    version="1.0.0"
)

# CORS 설정 (환경변수 사용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if USE_CONFIG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 임포트
from app.routers.openbanking_api import router as openbanking_router

# Mobile API 라우터 추가
try:
    from app.routers.mobile_api import router as mobile_router
    app.include_router(mobile_router)
    print("✅ Mobile API router loaded successfully!")
except ImportError as e:
    print(f"❌ Failed to load mobile API router: {e}")

# OpenBanking API 라우터 추가
app.include_router(openbanking_router)
print("✅ OpenBanking API router loaded")

# 다른 라우터들 (선택사항)
try:
    from app.routers.chat import router as chat_router
    app.include_router(chat_router)
    print("✅ Chat router loaded")
except ImportError:
    print("⚠️ Chat router not found (skipping)")

try:
    from app.routers.health import router as health_router
    app.include_router(health_router)
    print("✅ Health router loaded")
except ImportError:
    print("⚠️ Health router not found (skipping)")

try:
    from app.routers.rag import router as rag_router
    app.include_router(rag_router)
    print("✅ RAG router loaded")
except ImportError:
    print("⚠️ RAG router not found (skipping)")


# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "🚀 XAI Chatbot API with OpenBanking",
        "version": "2.0.0",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "mobile": "/api/v1/mobile",
            "openbanking": "/api/v1/openbanking",
            "test_sample": "/api/v1/openbanking/test/sample-data"
        }
    }

# 테스트 엔드포인트
@app.get("/test")
async def test():
    return {"status": "✅ Server is working!"}

# 환경변수 확인 엔드포인트 (개발용)
@app.get("/debug/config")
async def debug_config():
    """개발 환경에서 설정 확인용 (프로덕션에서는 제거)"""
    return {
        "env_loaded": os.path.exists(".env"),
        "has_xai_key": bool(os.getenv("XAI_API_KEY")),
        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "has_openbanking_id": bool(os.getenv("OPENBANKING_CLIENT_ID")),
        "server_host": os.getenv("SERVER_HOST", "not set"),
        "server_port": os.getenv("SERVER_PORT", "not set")
    }

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Starting XAI Chatbot API Server...")
    print("="*50)
    
    # 환경변수 체크
    if os.path.exists(".env"):
        print("✅ .env 파일을 찾았습니다")
    else:
        print("⚠️ .env 파일이 없습니다")
    
    # 설정 검증
    if validate_settings():
        print("✅ 설정 검증 완료")
        
        # 서버 정보 출력
        host = settings.server_host if USE_CONFIG else "0.0.0.0"
        port = settings.server_port if USE_CONFIG else 8000
        
        print(f"📍 Server URL: http://localhost:{port}")
        print("📚 API Docs: http://localhost:{port}/docs")
        print("🔍 Health Check: http://localhost:{port}/api/v1/mobile/health")
        print("🔍 Config Check: http://localhost:{port}/debug/config")
        print("="*50 + "\n")
        
        # 서버 실행
        uvicorn.run(app, host=host, port=port)
    else:
        print("❌ 서버 시작 실패: 설정을 확인하세요")
        print("1. .env 파일이 프로젝트 루트에 있는지 확인")
        print("2. 필수 API 키가 설정되었는지 확인")
