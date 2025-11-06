import json
from app.vector.chroma_client import get_chroma_collection
import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)



def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 상품목록 안쪽 구조 처리
    if isinstance(data, dict) and "상품목록" in data:
        data = data["상품목록"]
    return data

def insert_to_chroma(data):
    db = get_chroma_collection()
    count = 0
    for product in data:
        text = f"{product.get('상품명', '')} {product.get('기본정보', {}).get('상품설명', '')}"
        db.add_texts([text])
        count += 1
    print(f"{count}개의 상품이 ChromaDB에 저장되었습니다.")

if __name__ == "__main__":
    data = load_json("./data/거치식예금_통합.json")  # 파일명 맞게 수정
    insert_to_chroma(data)
