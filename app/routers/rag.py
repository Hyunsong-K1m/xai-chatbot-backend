# app/routers/rag.py
from fastapi import APIRouter
from pydantic import BaseModel
from scripts.rag_system import ask  # ｒａｇ 연결  여기서 연결

router = APIRouter()

class Question(BaseModel):
    question: str

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
