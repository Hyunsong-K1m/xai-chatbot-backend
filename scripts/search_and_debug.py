# 생성 전 임베딩된 문서 검색 및 출력 확인해보는 코드
import os
import pprint
from typing import List, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma  # ← 최신 버전 import 수정

from config import (
    PERSIST_DIRECTORY,
    COLLECTION_NAME,
    MODEL_NAME,
    MODEL_KWARGS,
    ENCODE_KWARGS,
    SEARCH_K,
)

# 1. 임베딩 모델 초기화
embeddings = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs=MODEL_KWARGS,
    encode_kwargs=ENCODE_KWARGS,
)

# 2. ChromaDB 연결
vectorstore = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)

# 3. Retriever 설정
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": SEARCH_K}
)

# 4. 문서 검색 함수 (최신 버전)
def search_docs(query: str):
    # 최신 방식: retriever.invoke(query)
    results = retriever.invoke(query)

    for i, doc in enumerate(results, 1):
        print(f"문서 {i}")
        print("메타데이터:")
        pprint.pprint(getattr(doc, "metadata", {}), indent=4)
        print("내용:")
        print(getattr(doc, "page_content", ""))
        print("-" * 50)
    return results

if __name__ == "__main__":
    search_docs("iM행복파트너예금 중도해지이자율 설명해줘")
