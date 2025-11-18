<<<<<<< HEAD
=======
# app/schemas/rag.py
from pydantic import BaseModel

class Question(BaseModel):
    question: str

class RAGResponse(BaseModel):
    question: str
    answer: str
>>>>>>> origin/test-fast-api
