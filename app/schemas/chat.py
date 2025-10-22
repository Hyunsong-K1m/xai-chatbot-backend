from pydantic import BaseModel
class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None
class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
