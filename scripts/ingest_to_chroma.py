# PDF -> 텍스트 -> 청킹 -> 임베딩 -> Chroma 저장 스크립트 자리표시자
import json
from app.vector.chroma_client import get_chroma_collection

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def insert_to_chroma(data):
    db = get_chroma_collection()
    for idx, product in enumerate(data["상품목록"]):
        text = f"{product['상품명']} {product.get('상품설명', '')}"
        db.add_texts([text], metadatas=[{
            "은행명": product["은행명"],
            "카테고리": data["카테고리"]
        }])

if __name__ == "__main__":
    data = load_json("./data/processed_chunks/대구은행_적립식예금.json")
    insert_to_chroma(data)
    print("DB 저장 완료")
