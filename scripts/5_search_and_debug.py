# 생성 전 임베딩된 문서 검색 및 출력 확인해보는 코드
import os
import pprint
from typing import List, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import PERSIST_DIRECTORY, COLLECTION_NAME, MODEL_NAME, MODEL_KWARGS, ENCODE_KWARGS, SEARCH_K

embeddings = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs=MODEL_KWARGS,
    encode_kwargs=ENCODE_KWARGS,
)

vectorstore = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)

retriever = vectorstore.as_retriever(search_type="similarity",
                                     search_kwargs={"k": SEARCH_K})

def search_docs(query: str):
    results = retriever.get_relevant_documents(query)

    for i, doc in enumerate(results, 1):
        print("메타데이터:")
        pprint.pprint(doc.metadata, indent=4)
        print("내용:")
        print(doc.page_content)
    return results

if __name__ == "__main__":
    search_docs("iM행복파트너예금 중도해지이자율 설명해줘")
