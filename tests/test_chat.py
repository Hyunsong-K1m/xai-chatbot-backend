def test_placeholder(): assert True
from app.vector.chroma_client import get_chroma_collection

db = get_chroma_collection()
results = db.similarity_search("직장인 대출", k=3)

for r in results:
    print(r.page_content)
