# 임베딩한거 내용 전체출력하는 코드
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from config import (
    PERSIST_DIRECTORY,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    MODEL_NAME,
    MODEL_KWARGS,
    ENCODE_KWARGS,
    SEARCH_K,
)

def main():
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS,
    )

    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    all_docs = vectorstore.get()
    ids = all_docs.get("ids", [])
    metadatas = all_docs.get("metadatas", [])
    documents = all_docs.get("documents", [])
    print("총 문서 수: {}".format(len(ids)))

    for i, (doc_id, meta, content) in enumerate(zip(ids, metadatas, documents), 1):
        print("문서 {0}".format(i))
        print("ID: {0}".format(doc_id))
        print("상품명: {0}".format(meta.get('product_name')))
        print("메타데이터: {0}".format(meta))
        print("내용 전체:\n{0}".format(content))
        print("{0}".format("-----------------------------------------"))

if __name__ == "__main__":
    main()
