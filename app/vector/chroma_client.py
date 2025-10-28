# FastAPI 서버에서 DB를 불러오는 모듈 py / 서버 실행시 이 코드로 ChromaDB 생성
import os 
import chromadb import Persistentlient #로컬경로에 DB 만듬 / 왜 못가져온대???
from langchain_community.vectorstores import chroma #백터DB 객체 생성
from langchain_huggingface import HuggingFaceEmbeddings #문장을 백터로 바꾸는 모델 

def get_chroma_client():
    path = os.getenv("HROMA_PATH", ".data/chroma")
    return Persistentlient(path)


def get_chroma_collectio():
    client = get_chroma_client()
    embeddings = HuggingFaceEmbeddings(model_name="nlpai-lab/KURE-v1") #모델 ipynb에 있는거 쓰기 ㅎ
    db = Chroma(client=client, collection_name="financial_products", embedding_fuction=embeddings)
                                       
                                
