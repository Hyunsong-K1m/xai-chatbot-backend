from fastapi import FastAPI
from app.routers import rag
from app.vector.chroma_client import get_chroma_collection

app = FastAPI()

@app.get("/")
def root():
    return {"message": "server running"}

@app.get("/test-search")
def test_search(query: str):
    db = get_chroma_collection()
    results = db.similarity_search(query, k=3)

    return {
        "query": query,
        "results": [r.page_content for r in results]
    }

app.include_router(rag.router, prefix="/api/v1")
