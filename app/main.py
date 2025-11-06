from fastapi import FastAPI
from app.routers import rag

app = FastAPI()

@app.get("/")
def root():
    return {"message": "서버 정상 동작 중"}

app.include_router(rag.router, prefix="/api/v1")
