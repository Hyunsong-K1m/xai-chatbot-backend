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
    results = db.query(query_texts=[query], n_results=3)
    return {"query": query, "results": results}

app.include_router(rag.router)
