from fastapi import APIRouter
from app.vector.chroma_client import get_chroma_collection

router = APIRouter()  # ← 이 줄이 반드시 제일 위에 있어야 함

@router.get("/check-db")
def check_db():
    db = get_chroma_collection()
    return {"documents": db._collection.count()}

# 테스트용 RAG 질의응답 라우트 예시
from pydantic import BaseModel

class Question(BaseModel):
    question: str

@router.post("/rag-query")
def rag_query(req: Question):
    db = get_chroma_collection()
    results = db.similarity_search(req.question, k=3)
    context = " ".join([r.page_content for r in results])
    answer = f"검색된 관련 내용: {context[:300]}..."
    return {"answer": answer}
