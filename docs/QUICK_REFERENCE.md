# REST API 빠른 참조 가이드

## 🎯 핵심 요약

### 프로젝트 구조 (한눈에 보기)

```
📦 xai-chatbot-backend
│
├── 🌐 app/routers/          ← API 엔드포인트 (4개 라우터)
│   ├── health.py            1개 엔드포인트 (헬스체크)
│   ├── rag.py               3개 엔드포인트 (RAG 시스템)
│   ├── mobile_api.py        6개 엔드포인트 (모바일 채팅)
│   └── openbanking_api.py   7개 엔드포인트 (오픈뱅킹)
│
├── 📝 app/schemas/          ← 데이터 검증 (Pydantic)
│   ├── chat.py              ChatRequest, ChatResponse
│   └── rag.py               Question, RAGResponse
│
├── 🔧 app/services/         ← 비즈니스 로직 (Placeholder)
├── 🗄️ app/models/           ← DB 모델 (Placeholder)
├── 💾 app/repositories/     ← 데이터 접근 (Placeholder)
│
├── 🧠 app/vector/           ← 벡터 DB
│   └── chroma_client.py     ChromaDB 클라이언트
│
├── ⚙️ app/core/             ← 유틸리티
│   └── errors.py            에러 핸들러
│
├── 🚀 app/main.py           ← FastAPI 앱 진입점
└── ⚙️ app/config.py         ← 전역 설정
```

---

## 📍 전체 API 엔드포인트 (17개)

### 1. Health Check (1개)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/health` | 서버 상태 확인 |

### 2. RAG System (3개)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/check-db` | ChromaDB 문서 수 확인 |
| POST | `/api/v1/rag-query` | LLM 질의응답 (GPT-4o) |
| POST | `/api/v1/rag-search` | 벡터 검색만 (LLM 없음) |

### 3. Mobile API (6개)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/mobile/health` | 모바일 API 상태 |
| POST | `/api/v1/mobile/session` | 채팅 세션 생성 |
| POST | `/api/v1/mobile/chat` | 메시지 전송 (OpenAI/XAI) |
| GET | `/api/v1/mobile/session/{id}/history` | 대화 기록 조회 |
| DELETE | `/api/v1/mobile/session/{id}` | 세션 삭제 |
| POST | `/api/v1/mobile/rag/query` | RAG 검색 (Mock) |

### 4. OpenBanking API (7개)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/openbanking/health` | 오픈뱅킹 상태 |
| POST | `/api/v1/openbanking/authorize` | OAuth 인증 URL 생성 |
| GET | `/api/v1/openbanking/callback` | OAuth 콜백 처리 |
| POST | `/api/v1/openbanking/account/list` | 계좌 목록 조회 |
| POST | `/api/v1/openbanking/account/balance` | 잔액 조회 |
| POST | `/api/v1/openbanking/account/transactions` | 거래내역 조회 |
| GET | `/api/v1/openbanking/test/sample-data` | 테스트 데이터 |

---

## 🔄 각 폴더의 역할

| 폴더 | 역할 | 현재 상태 | 핵심 파일 |
|------|------|----------|---------|
| **routers/** | HTTP 요청 처리 | ✅ 완료 | rag.py (44줄)<br/>mobile_api.py (330줄)<br/>openbanking_api.py (419줄) |
| **schemas/** | 데이터 검증 | ⚠️ 부분 | chat.py (7줄)<br/>rag.py (8줄) |
| **services/** | 비즈니스 로직 | ❌ Placeholder | 실제 로직은 `scripts/rag_system.py`에 있음 |
| **models/** | DB 모델 | ❌ Placeholder | 향후 SQLModel 구현 예정 |
| **repositories/** | 데이터 접근 | ❌ Placeholder | 향후 CRUD 구현 예정 |
| **vector/** | 벡터 DB | ✅ 완료 | chroma_client.py (26줄) |
| **core/** | 유틸리티 | ✅ 완료 | errors.py (98줄) |

---

## 📊 주요 기술 스택

### Backend
- **FastAPI 0.104.1** - 비동기 웹 프레임워크
- **Uvicorn 0.24.0** - ASGI 서버
- **Pydantic 2.5.0** - 데이터 검증

### AI/ML
- **LangChain** - RAG 파이프라인
- **OpenAI GPT-4o** - LLM
- **HuggingFace** - 임베딩 (`nlpai-lab/KURE-v1`)
- **ChromaDB** - 벡터 DB

### Database
- **SQLite** - 개발용 DB (향후 PostgreSQL)
- **ChromaDB** - 벡터 저장소

### External APIs
- **OpenAI Chat Completions** - 질의응답
- **금융결제원 오픈뱅킹** - 금융 API

---

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력
```

### 2. 데이터 준비
```bash
# ChromaDB에 금융상품 데이터 삽입
python scripts/insert_to_chroma.py
```

### 3. 서버 실행
```bash
# 개발 모드 (자동 재시작)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 💡 API 사용 예시

### RAG 질의응답
```bash
curl -X POST "http://localhost:8000/api/v1/rag-query" \
  -H "Content-Type: application/json" \
  -d '{"question": "높은 금리 예금 추천해줘"}'
```

**응답**:
```json
{
  "question": "높은 금리 예금 추천해줘",
  "answer": "현재 가장 높은 금리는 신한은행의 거치식예금으로..."
}
```

### 모바일 채팅
```bash
# 1. 세션 생성
curl -X POST "http://localhost:8000/api/v1/mobile/session" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'

# 2. 메시지 전송
curl -X POST "http://localhost:8000/api/v1/mobile/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 오픈뱅킹 인증
```bash
# 1. 인증 URL 생성
curl -X POST "http://localhost:8000/api/v1/openbanking/authorize" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'

# 2. 계좌 목록 조회
curl -X POST "http://localhost:8000/api/v1/openbanking/account/list" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

---

## 🗂️ 데이터 흐름

### RAG 질의응답 흐름
```
Client
  ↓ POST /api/v1/rag-query {"question": "..."}

Router (rag.py)
  ↓ Pydantic 검증 (Question 모델)

RAG System (scripts/rag_system.py)
  ↓ 질문 전처리
  ↓ ChromaDB 검색 (k=10)
  ↓ 문서 포맷팅
  ↓ 프롬프트 생성
  ↓ OpenAI GPT-4o 호출

Response
  ↓ {"question": "...", "answer": "..."}
```

### 오픈뱅킹 인증 흐름
```
1. Client → POST /authorize
   {"user_id": "user123"}

2. Backend → 인증 URL 생성
   state 저장 (CSRF 방지)

3. Backend → Client
   {"auth_url": "https://...", "state": "..."}

4. User → 브라우저에서 auth_url 접속
   계좌 선택 및 인증

5. OpenBanking → GET /callback?code=xxx&state=yyy

6. Backend → code로 Access Token 발급
   Token 저장

7. Client → POST /account/list
   저장된 Token으로 계좌 조회
```

---

## 🔧 주요 설정 파일

### .env (환경변수)
```bash
# AI API 키
OPENAI_API_KEY=sk-proj-...

# 오픈뱅킹
OPENBANKING_CLIENT_ID=your_client_id
OPENBANKING_CLIENT_SECRET=your_secret
OPENBANKING_CALLBACK_URL=http://localhost:8000/api/v1/openbanking/callback

# 서버
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG_MODE=True
```

### app/config.py (주요 설정)
```python
BASE_DIR = Path(__file__).resolve().parent.parent

# 경로 설정 (Windows/Linux 호환)
JSON_PATH = str(BASE_DIR / "data" / "json")
PERSIST_DIRECTORY = str(BASE_DIR / "data" / "chroma")

# AI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "nlpai-lab/KURE-v1"  # 한국어 임베딩 모델
```

---

## 📦 데이터 구조

### ChromaDB 저장 데이터
```
Collection: financial_products
├── 거치식예금 (449KB, ~200개 상품)
├── 입출금자유예금 (838KB, ~400개 상품)
├── 적립식예금 (768KB, ~350개 상품)
└── 주택청약 (70KB, ~50개 상품)

총 ~1,000개 금융상품 임베딩
벡터 차원: 768 (KURE-v1 모델)
```

### 임베딩 데이터 포맷
```
은행명: 신한은행
상품명: S드림 적금
상품유형: 적립식예금
상품설명: 매월 일정 금액을 적립하는...
기본금리: 3.5%
우대이자율: 0.5%
최고이자율: 4.0%
...
```

---

## 🐛 디버깅 팁

### ChromaDB 상태 확인
```bash
curl http://localhost:8000/api/v1/check-db
# {"documents": 1234}
```

### 로그 확인
```python
# app/core/logging.py 설정
logging.basicConfig(level=logging.INFO)

# Router에서 로깅
logger.info(f"RAG query: {question}")
logger.error(f"Error: {e}")
```

### 에러 응답 포맷
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력 데이터 검증 실패",
    "details": {"errors": [...]}
  }
}
```

---

## 📚 관련 문서

- [ARCHITECTURE.md](../ARCHITECTURE.md) - 전체 아키텍처 상세 가이드
- [API_FLOW.md](./API_FLOW.md) - 플로우 다이어그램 (Mermaid)
- [REST_API_STRUCTURE.md](./REST_API_STRUCTURE.md) - 폴더별 상세 설명
- [README.md](../README.md) - 프로젝트 개요

---

## ✅ 체크리스트

### 개발 환경 설정
- [ ] Python 3.10+ 설치
- [ ] 가상환경 생성 및 활성화
- [ ] `pip install -r requirements.txt`
- [ ] `.env` 파일 설정 (API 키)
- [ ] ChromaDB 데이터 삽입

### API 테스트
- [ ] `GET /api/v1/health` - 서버 정상 동작
- [ ] `GET /api/v1/check-db` - ChromaDB 문서 수 확인
- [ ] `POST /api/v1/rag-query` - RAG 질의응답
- [ ] `POST /api/v1/mobile/chat` - 모바일 채팅
- [ ] Swagger UI 확인 (http://localhost:8000/docs)

### 프로덕션 배포
- [ ] PostgreSQL 마이그레이션
- [ ] Redis 캐싱 설정
- [ ] JWT 인증 구현
- [ ] HTTPS 설정
- [ ] 로그 수집 (Sentry, CloudWatch)
- [ ] 모니터링 (Prometheus, Grafana)

---

**작성일**: 2025-01-19
**버전**: 1.0.0
