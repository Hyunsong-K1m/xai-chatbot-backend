import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import PERSIST_DIRECTORY, COLLECTION_NAME, MODEL_NAME, MODEL_KWARGS, ENCODE_KWARGS

def get_chroma_collection():
    """
    ChromaDB 벡터 스토어 인스턴스를 반환합니다.
    환경변수 및 config.py 설정을 사용합니다.
    """
    # 임베딩 모델 설정
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS
    )

    # ChromaDB 연결
    db = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )

    return db
