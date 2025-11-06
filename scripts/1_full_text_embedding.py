# 하나의 상품당 하나의 청크로 처리(full txt 청킹)
import os
import json
from pathlib import Path
from typing import Any, Dict, List

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import JSON_PATH, PERSIST_DIRECTORY, COLLECTION_NAME, MODEL_NAME, MODEL_KWARGS, ENCODE_KWARGS

def load_json(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {p}")
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # 수정,
    if isinstance(data, dict) and "상품목록" in data:
        data = data["상품목록"]
    elif not isinstance(data, list):
        raise ValueError("JSON 루트가 list 형태가 아니고 '상품목록' 키도 없습니다.")
    return data


def safe_get_product_name(product: Dict[str, Any]) -> str:
    try:
        return product["상품 개요 및 특징"]["상품명"]
    except Exception:
        pass
    for k, v in product.items():
        if isinstance(v, dict) and "상품명" in v and isinstance(v["상품명"], str):
            return v["상품명"]
        if k == "상품명" and isinstance(v, str):
            return v
    return None

def flatten_to_text(obj: Any, prefix: str = "") -> str:
    lines: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k)
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(flatten_to_text(v, prefix + "  "))
            else:
                lines.append(f"{prefix}{key}: {v}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj, 1):
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}- 항목 {i}:")
                lines.append(flatten_to_text(v, prefix + "  "))
            else:
                lines.append(f"{prefix}- {v}")
    else:
        lines.append(f"{prefix}{obj}")
    return "\n".join(lines)

def build_documents(products: List[Dict[str, Any]], source_path: str) -> List[Document]:
    docs: List[Document] = []
    total = len(products)
    for idx, product in enumerate(products):
        name = safe_get_product_name(product) or f"UNKNOWN_PRODUCT_{idx+1}"
        content = flatten_to_text(product)

        docs.append(
            Document(
                page_content=content,
                metadata={
                    "product_name": name,
                    "source_file": os.path.basename(source_path),
                    "chunking": "one_product_per_document",
                    "lang": "ko",
                    "index": idx,
                },
            )
        )
    return docs

def main():
    products = load_json(JSON_PATH)
    total_docs = len(products)
    print("총 {n}개 상품 로드됨".format(n=total_docs))

    documents = build_documents(products, JSON_PATH)

    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS,
    )

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        collection_name=COLLECTION_NAME,
    )
    vectorstore.persist()
    print(total_docs)
    print("문서 임베딩 및 저장 완료")

if __name__ == "__main__":
    main()
