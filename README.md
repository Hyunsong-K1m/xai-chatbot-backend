# 2025.11.08
# iM Bank 백엔드 (FastAPI 기반)  
담당: 김현송  
현재 상태 기준 README


---

## 현재 진행 상황

- FastAPI 서버 기본 구조 및 폴더 세팅 완료
- `.env` 설정 완료 (`OPENAI_API_KEY`, `CHROMA_PATH`, `MODEL_NAME`)
- `insert_to_chroma.py` 실행 중 오류 발생 (DB 삽입 테스트 단계)
- LLM 인혜님이 만들어주신 rag 연결 중
- 서버는 로컬(Ubuntu 22.04, VMware) 환경에서 실행 중

---

## 서버 실행 방법

### 1. 가상환경 실행
cd ~/fastapi-backend
source .venv/bin/activate

## 2. 환경 설치
pip install -r requirements.txt

## 3. 서버실행
uvicorn app.main:app --reload

## 4. 실행 후 확인
브라우저에서: http://127.0.0.1:8000/docs
/docs에서 Swagger 자동 문서 확인 가능

---

## SSH 접속 정보

서버: VMware Ubuntu 22.04
접속 명령:
ssh xai@<IP주소>

(IP는 hostname -I로 확인 가능)
192.168.219.104

비밀번호:
ubuntu

접속 후 경로: /home/xai/fastapi-backend







