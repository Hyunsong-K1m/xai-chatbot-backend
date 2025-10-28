# DB를 매일 새로 연결할 필요없이 자동으로 함수 실행해서 DB 객체를 db에 넣어주는 py
from app.vector.chroma_client import get_chroma_collection

def get_vectorstore(): 
    return get_chroma_collection()
