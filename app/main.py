from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import rag, health, mobile_api, openbanking_api
from app.vector.chroma_client import get_chroma_collection

APP_NAME = "finance-qa"
API_PREFIX = "/api/v1"
CORS = ["*"]

app = FastAPI(title=APP_NAME)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "서버 정상 동작 중"}

@app.get("/test-search")
def test_search(query: str):
    """ChromaDB 벡터 검색 테스트용 엔드포인트"""
    db = get_chroma_collection()
    results = db.similarity_search(query, k=3)
    return {
        "query": query,
        "results": [r.page_content for r in results]
    }

# 라우터 등록
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(rag.router, prefix=API_PREFIX)
app.include_router(openbanking_api.router)  # prefix는 라우터에서 정의됨
app.include_router(mobile_api.router)  # prefix는 라우터에서 정의됨

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
