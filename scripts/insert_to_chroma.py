import json
import glob
from app.vector.chroma_client import get_chroma_collection


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "상품목록" in data:
        data = data["상품목록"]
    return data


def safe_get(d, key, default=""):
    """딕셔너리 안전 접근용 헬퍼"""
    if isinstance(d, dict):
        return d.get(key, default)
    return default


def insert_to_chroma(data):
    db = get_chroma_collection()
    count = 0

    for product in data:
        기본정보 = product.get("기본정보", {}) or {}
        금리정보 = product.get("금리정보", {}) or {}
        계약정보 = product.get("계약정보", {}) or {}
        청약정보 = product.get("청약및정부지원정보", {}) or {}
        위험 = product.get("위험유의사항", {}) or {}

        # 기본이자율 처리
        기본이자율_text = ""
        if isinstance(금리정보.get("기본이자율"), list):
            rates = []
            for r in 금리정보["기본이자율"]:
                if isinstance(r, dict):
                    기간 = r.get("계약기간", "")
                    이율 = r.get("이율", "")
                    rates.append(f"{기간} {이율}")
            기본이자율_text = ", ".join(rates)

        # 안전한 접근으로 텍스트 구성
        text = (
            f"상품명: {safe_get(product, '상품명')}\n"
            f"상품유형: {safe_get(product, '상품유형')}\n"
            f"상품설명: {safe_get(기본정보, '상품설명')}\n"
            f"가입대상: {safe_get(기본정보, '가입대상')}\n"
            f"가입한도: {safe_get(기본정보, '가입한도')}\n"
            f"이자지급시기: {safe_get(기본정보, '이자지급시기')}\n"
            f"예금자보호: {safe_get(기본정보.get('예금자보호', {}), '보호여부')}\n"
            f"기본금리: {기본이자율_text}\n"
            f"최고이자율: {safe_get(safe_get(금리정보, '최고이자율', {}), '총이율')}\n"
            f"중도해지이율: {safe_get(금리정보, '중도해지이율')}\n"
            f"소득공제: {safe_get(safe_get(계약정보, '소득공제', {}), '적용여부')}, "
            f"{safe_get(safe_get(계약정보, '소득공제', {}), '공제한도')}\n"
            f"청약적용여부: {safe_get(청약정보, '청약적용여부')}\n"
            f"정부지원형: {safe_get(청약정보, '정부지원형')}\n"
            f"위험유의사항: {safe_get(위험, '청약자격상실')}, {safe_get(위험, '소득공제추징')}"
        )

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
