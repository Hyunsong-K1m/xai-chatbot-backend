from app.vector.chroma_client import get_chroma_collection

db = get_chroma_collection()
docs = db.get(limit=3)
print(len(docs["ids"]))
print(docs["documents"][:1])
