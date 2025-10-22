from pydantic import BaseModel
class UploadResponse(BaseModel):
    ok: bool
    doc_id: str | None = None
class RAGQuery(BaseModel):
    question: str
