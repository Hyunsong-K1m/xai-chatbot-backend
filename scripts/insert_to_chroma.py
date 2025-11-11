import json
import glob
from app.vector.chroma_client import get_chroma_collection


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        if "상품목록" in data:
            data = data["상품목록"]
        elif "products" in data:
            data = data["products"]
        else:
            data = [data]
    return data


def flatten_dict(d, parent_key="", sep="_"):
    """중첩 딕셔너리를 flat하게 펴줌 (예: 금리정보_기본이자율_이율)"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 리스트는 최대 3개 항목만 요약 저장
            joined = ", ".join([str(i)[:100] for i in v[:3]])
            items.append((new_key, joined))
        else:
            items.append((new_key, str(v)))
    return dict(items)


def insert_to_chroma(data):
    db = get_chroma_collection()
    count = 0

    for product in data:
        flat = flatten_dict(product)

        text_parts = [
            f"은행명: {flat.get('은행명', '')}",
            f"상품명: {flat.get('상품명', '')}",
            f"상품유형: {flat.get('상품유형', '')}",
            f"상품설명: {flat.get('기본정보_상품설명', '')}",
            f"가입대상: {flat.get('기본정보_가입대상', '')}",
            f"기본금리: {flat.get('금리정보_기본이자율', '')}",
            f"우대이자율: {flat.get('금리정보_우대이자율', '')}",
            f"최고이자율: {flat.get('금리정보_최고이자율_총이율', '')}",
            f"중도해지이율: {flat.get('금리정보_중도해지이율', '')}",
            f"정부지원형: {flat.get('청약및정부지원정보_정부지원형', '')}",
            f"청약적용여부: {flat.get('청약및정부지원정보_청약적용여부', '')}",
            f"위험유의사항: {flat.get('위험유의사항', '')}",
        ]

        # join 후 길이 제한
        text = "\n".join([t for t in text_parts if t.strip()])[:3000]
        db.add_texts([text])
        count += 1

    db.persist()
    print(f"{count}개의 상품이 ChromaDB에 저장되었습니다.")


if __name__ == "__main__":
    all_data = []
    json_files = glob.glob("/home/xai/fastapi-backend/data/json/*.json")
    for file in json_files:
        data = load_json(file)
        print(f"{file} → {len(data)}개 로드")
        all_data.extend(data)

    print(f"불러온 전체 상품 수: {len(all_data)}")
    insert_to_chroma(all_data)
