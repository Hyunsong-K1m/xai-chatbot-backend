from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
from app.routers.openbanking_api import router as openbanking_router

app = FastAPI(
    title="XAI Chatbot API",
    description="XAI Chatbot Backend with Mobile API Support",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mobile API 라우터 추가
try:
    from app.routers.mobile_api import router as mobile_router
    app.include_router(mobile_router)
    print("✅ Mobile API router loaded successfully!")
except ImportError as e:
    print(f"❌ Failed to load mobile API router: {e}")

# 다른 라우터들 (선택사항)
app.include_router(openbanking_router)
print("✅ OpenBanking API router loaded")

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

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Starting XAI Chatbot API Server...")
    print("="*50)
    print("📍 Server URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/v1/mobile/health")
    print("="*50 + "\n")
    
    # reload 없이 실행 (경고 메시지 없애기)
    uvicorn.run(app, host="0.0.0.0", port=8000)
