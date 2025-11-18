from fastapi import APIRouter
from pydantic import BaseModel
from app.vector.chroma_client import get_chroma_collection
from scripts.rag_system import ask

router = APIRouter()

class Question(BaseModel):
    question: str

@router.get("/check-db")
def check_db():
    """ChromaDB 상태 확인"""
    db = get_chroma_collection()
    return {"documents": db._collection.count()}

@router.post("/rag-query")
def rag_query(q: Question):
    """
    사용자의 질문을 받아 RAG 시스템을 통해 LLM 응답을 생성.
    """
    try:
        answer = ask(q.question)
        return {"question": q.question, "answer": answer}
    except Exception as e:
        return {"error": str(e)}

@router.post("/rag-search")
def rag_search(q: Question):
    """
    벡터 DB에서 관련 문서만 검색 (LLM 응답 없이)
    """
    try:
        db = get_chroma_collection()
        results = db.similarity_search(q.question, k=3)
        context = " ".join([r.page_content for r in results])
        return {
            "question": q.question,
            "results": [r.page_content for r in results],
            "summary": f"검색된 관련 내용: {context[:300]}..."
        }
    except Exception as e:
        return {"error": str(e)}
