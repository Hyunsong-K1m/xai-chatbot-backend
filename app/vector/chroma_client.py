import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ChromaDB 경로 설정
path = "/home/xai/fastapi-backend/data/chroma"
COLLECTION_NAME = "financial_products"

def get_chroma_collection():
    # 1️임베딩 모델
    embeddings = HuggingFaceEmbeddings(
        model_name="nlpai-lab/KURE-v1",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # 2️Chroma DB 연결
    db = Chroma(
        persist_directory="/home/xai/fastapi-backend/data/chroma",
        collection_name="financial_products",
        embedding_function=embeddings
    )

    return db
