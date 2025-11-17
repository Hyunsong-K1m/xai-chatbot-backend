import os
from chromadb import PersistentClient
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def get_chroma_client():
    path = os.getenv("CHROMA_PATH", "./data/chroma")
    return PersistentClient(path)


def get_chroma_collection():
    client = get_chroma_client()
    embeddings = HuggingFaceEmbeddings(model_name="nlpai-lab/KURE-v1")
    db = Chroma(
        client=client,
        collection_name="financial_products",
        embedding_function=embeddings
    )
    return db
