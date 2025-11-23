# REST API 구조 가이드

## 📋 목차
1. [전체 구조 개요](#전체-구조-개요)
2. [폴더별 상세 설명](#폴더별-상세-설명)
3. [API 요청 흐름](#api-요청-흐름)
4. [주요 API 엔드포인트](#주요-api-엔드포인트)
5. [데이터 모델](#데이터-모델)

---

## 전체 구조 개요

```
app/
├── main.py                 # FastAPI 애플리케이션 진입점
├── config.py               # 전역 설정 (환경변수, 경로)
├── deps.py                 # 의존성 주입 (Dependency Injection)
│
├── routers/                # 🌐 API 엔드포인트 정의 (Router Layer)
│   ├── health.py           #   ✅ 헬스체크 API
│   ├── rag.py              #   🤖 RAG 질의응답 API
│   ├── mobile_api.py       #   📱 모바일 채팅 API
│   └── openbanking_api.py  #   🏦 오픈뱅킹 API
│
├── schemas/                # 📝 데이터 검증 스키마 (Pydantic Models)
│   ├── chat.py             #   채팅 요청/응답 모델
│   ├── rag.py              #   RAG 요청/응답 모델
│   └── common.py           #   공통 스키마 (Placeholder)
│
├── services/               # 🔧 비즈니스 로직 (Service Layer)
│   ├── chat_service.py     #   채팅 로직 (Placeholder)
│   └── rag_service.py      #   RAG 로직 (Placeholder)
│
├── models/                 # 🗄️ 데이터베이스 모델 (SQLModel)
│   ├── chat.py             #   채팅 세션/메시지 모델 (Placeholder)
│   └── doc.py              #   문서 모델 (Placeholder)
│
├── repositories/           # 💾 데이터 접근 계층 (Repository Pattern)
│   ├── chat_repo.py        #   채팅 CRUD (Placeholder)
│   └── doc_repo.py         #   문서 CRUD (Placeholder)
│
├── vector/                 # 🧠 벡터 DB 관련
│   ├── chroma_client.py    #   ChromaDB 클라이언트
│   └── embedder.py         #   임베딩 래퍼 (Placeholder)
│
└── core/                   # ⚙️ 핵심 유틸리티
    ├── errors.py           #   에러 핸들러
    ├── logging.py          #   로깅 설정
    └── config.py           #   코어 설정 (Placeholder)
```

---

## 폴더별 상세 설명

### 1️⃣ **app/routers/** - API 엔드포인트 (Controller)

> HTTP 요청 처리 → 서비스 호출 → 응답 반환

#### **health.py** (4줄)
- **엔드포인트**: `GET /api/v1/health`
- **역할**: 서버 상태 확인 (로드 밸런서, 모니터링용)
- **응답**: `{"status": "ok"}`

---

#### **rag.py** (44줄)
**API 목록** (3개):

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/check-db` | ChromaDB 문서 수 확인 |
| POST | `/api/v1/rag-query` | LLM 질의응답 (GPT-4o) |
| POST | `/api/v1/rag-search` | 벡터 검색만 (LLM X) |

**핵심 로직**:
```python
from scripts.rag_system import ask

@router.post("/rag-query")
def rag_query(q: Question):
    answer = ask(q.question)  # 벡터 검색 → GPT-4o
    return {"question": q.question, "answer": answer}
```

**처리 흐름**: 질문 → ChromaDB 검색 (k=10) → 프롬프트 생성 → OpenAI API → 답변

---

#### **mobile_api.py** (330줄)
**API 목록** (6개):

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/mobile/health` | API 상태 |
| POST | `/api/v1/mobile/session` | 세션 생성 |
| POST | `/api/v1/mobile/chat` | 메시지 전송 |
| GET | `/api/v1/mobile/session/{id}/history` | 대화 기록 |
| DELETE | `/api/v1/mobile/session/{id}` | 세션 삭제 |
| POST | `/api/v1/mobile/rag/query` | RAG 검색 |

**핵심 컴포넌트**:
```python
# 1. 세션 관리 (메모리)
SessionManager: {session_id: {messages, created_at, ...}}

# 2. AI 서비스 (OpenAI/XAI)
RealChatService:
  - OpenAI gpt-3.5-turbo / XAI grok-beta
  - 대화 컨텍스트 5개 유지
```

---

#### **openbanking_api.py** (419줄)
**API 목록** (7개):

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/openbanking/health` | 상태 확인 |
| POST | `/api/v1/openbanking/authorize` | OAuth URL 생성 |
| GET | `/api/v1/openbanking/callback` | OAuth 콜백 |
| POST | `/api/v1/openbanking/account/list` | 계좌 목록 |
| POST | `/api/v1/openbanking/account/balance` | 잔액 조회 |
| POST | `/api/v1/openbanking/account/transactions` | 거래내역 |
| GET | `/api/v1/openbanking/test/sample-data` | 테스트 데이터 |

**핵심 컴포넌트**:
```python
OpenBankingConfig:
  - BASE_URL: https://testapi.openbanking.or.kr
  - CLIENT_ID, CLIENT_SECRET

TokenStore (메모리):
  - tokens: {user_id: token_info}
  - states: {state: user_info}  # CSRF 방지
```

**OAuth 플로우**:
```
1. POST /authorize → 인증 URL 생성
2. User → 오픈뱅킹 페이지 → 계좌 선택
3. GET /callback → Access Token 발급
4. POST /account/* → 계좌 정보 조회
```

---

### 2️⃣ **app/schemas/** - 데이터 검증 (Pydantic)

> 요청/응답 데이터 검증 및 직렬화

#### **chat.py** (7줄)
```python
class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
```

#### **rag.py** (8줄)
```python
class Question(BaseModel):
    question: str

class RAGResponse(BaseModel):
    question: str
    answer: str
```

**역할**: 타입 검증, JSON 직렬화, Swagger 자동 생성

---

### 3️⃣ **app/services/** - 비즈니스 로직

> 복잡한 비즈니스 규칙, 외부 API 호출

**현재 상태**: ❌ Placeholder (미구현)
- `chat_service.py` - GPT 호출 및 대화 저장
- `rag_service.py` - PDF 임베딩/검색

**실제 로직 위치**: `scripts/rag_system.py` (419줄)

---

### 4️⃣ **app/models/** - 데이터베이스 모델

> SQLModel 기반 DB 테이블 정의

**현재 상태**: ❌ Placeholder (미구현)
- `chat.py` - ChatSession, ChatMessage
- `doc.py` - Document, Chunk

**향후 구현**: SQLModel로 DB 스키마 정의

---

### 5️⃣ **app/repositories/** - 데이터 접근 계층

> CRUD 작업 캡슐화 (Repository Pattern)

**현재 상태**: ❌ Placeholder (미구현)
- `chat_repo.py` - 채팅 CRUD
- `doc_repo.py` - 문서 CRUD

**장점**: DB 로직 분리, 테스트 용이, DB 교체 쉬움

---

### 6️⃣ **app/vector/** - 벡터 DB

> ChromaDB 연결 및 임베딩 관리

#### **chroma_client.py** (26줄) ✅
```python
def get_chroma_collection():
    embeddings = HuggingFaceEmbeddings(
        model_name="nlpai-lab/KURE-v1",  # 한국어 특화
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    db = Chroma(
        persist_directory="./data/chroma",
        collection_name="financial_products",
        embedding_function=embeddings
    )
    return db
```

**용도**: RAG 시스템에서 벡터 검색 수행

---

### 7️⃣ **app/core/** - 유틸리티

> 에러 핸들러, 로깅, 설정

#### **errors.py** (98줄) ✅
```python
class APIException(Exception):
    status_code, error_code, message, details

# 에러 핸들러 4개
- api_exception_handler
- http_exception_handler
- validation_exception_handler
- general_exception_handler
```

**에러 응답**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력 데이터 검증 실패",
    "details": {...}
  }
}
```

---

### 8️⃣ **app/main.py** - 진입점 (44줄) ✅

```python
app = FastAPI(title="finance-qa")

# CORS 설정
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# 라우터 등록 (4개)
app.include_router(health.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(openbanking_api.router)
app.include_router(mobile_api.router)
```

**역할**: FastAPI 앱 생성, 미들웨어 설정, 라우터 통합

---

### 9️⃣ **app/config.py** - 설정 (48줄) ✅

```python
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "finance-qa"
    OPENAI_API_KEY: str
    OPENBANKING_CLIENT_ID: str
    CHROMA_PATH: str = str(BASE_DIR / "data" / "chroma")
```

**주요 설정**:
- 경로 (Windows/Linux 호환)
- API 키 (환경변수)
- 임베딩 모델: `nlpai-lab/KURE-v1`

---

### 🔟 **app/deps.py** - 의존성 주입 (6줄) ✅

```python
def get_vectorstore():
    return get_chroma_collection()
```

**용도**: FastAPI Depends로 자동 주입

---

## API 요청 흐름

### 예시: RAG 질의응답 요청

```
1. Client
   ↓ POST /api/v1/rag-query
   ↓ {"question": "높은 금리 예금 추천해줘"}

2. FastAPI Middleware
   ↓ CORS 검증
   ↓ 로깅

3. Router Layer (app/routers/rag.py)
   ↓ @router.post("/rag-query")
   ↓ def rag_query(q: Question)  ← Pydantic 검증

4. Service Layer (scripts/rag_system.py)
   ↓ answer = ask(q.question)
   ↓
   ├─ 질문 전처리
   ├─ ChromaDB 벡터 검색 (k=10)
   ├─ 문서 포맷팅
   ├─ 프롬프트 생성
   └─ OpenAI GPT-4o 호출

5. Data Layer
   ↓ ChromaDB: similarity_search()
   ↓ OpenAI API: chat.completions.create()

6. Response
   ↓ {"question": "...", "answer": "AI 답변"}
   ↓
   Client
```

---

## 주요 API 엔드포인트 정리

| 카테고리 | 메서드 | 경로 | 파일 | 설명 |
|---------|--------|------|------|------|
| **헬스체크** | GET | `/api/v1/health` | health.py | 서버 상태 확인 |
| **RAG** | GET | `/api/v1/check-db` | rag.py | ChromaDB 문서 수 |
| **RAG** | POST | `/api/v1/rag-query` | rag.py | LLM 질의응답 |
| **RAG** | POST | `/api/v1/rag-search` | rag.py | 벡터 검색만 |
| **모바일** | POST | `/api/v1/mobile/session` | mobile_api.py | 세션 생성 |
| **모바일** | POST | `/api/v1/mobile/chat` | mobile_api.py | 채팅 메시지 |
| **모바일** | GET | `/api/v1/mobile/session/{id}/history` | mobile_api.py | 히스토리 조회 |
| **오픈뱅킹** | POST | `/api/v1/openbanking/authorize` | openbanking_api.py | OAuth 인증 URL |
| **오픈뱅킹** | GET | `/api/v1/openbanking/callback` | openbanking_api.py | OAuth 콜백 |
| **오픈뱅킹** | POST | `/api/v1/openbanking/account/list` | openbanking_api.py | 계좌 목록 |
| **오픈뱅킹** | POST | `/api/v1/openbanking/account/balance` | openbanking_api.py | 잔액 조회 |
| **오픈뱅킹** | POST | `/api/v1/openbanking/account/transactions` | openbanking_api.py | 거래내역 |

---

## 데이터 모델

### Pydantic Models (schemas/)

#### ChatRequest
```python
{
  "message": "string",
  "session_id": "int | null"
}
```

#### Question
```python
{
  "question": "string"
}
```

#### RAGResponse
```python
{
  "question": "string",
  "answer": "string"
}
```

### OpenBanking Models

#### BalanceRequest
```python
{
  "user_id": "string",
  "fintech_use_num": "string"
}
```

#### TransactionRequest
```python
{
  "user_id": "string",
  "fintech_use_num": "string",
  "from_date": "YYYYMMDD",
  "to_date": "YYYYMMDD"
}
```

---

## 구현 상태 요약

| 폴더 | 구현 상태 | 파일 수 | 설명 |
|------|----------|---------|------|
| **routers/** | ✅ 완료 | 5개 | API 엔드포인트 모두 구현 |
| **schemas/** | ⚠️ 부분 | 3개 | RAG, Chat 구현 / Common은 Placeholder |
| **services/** | ❌ 미구현 | 2개 | 모두 Placeholder (로직은 scripts/에 있음) |
| **models/** | ❌ 미구현 | 2개 | 모두 Placeholder |
| **repositories/** | ❌ 미구현 | 2개 | 모두 Placeholder |
| **vector/** | ✅ 완료 | 1개 | chroma_client 구현 완료 |
| **core/** | ✅ 완료 | 1개 | errors.py 구현 완료 |

**실제 비즈니스 로직 위치**:
- RAG 시스템: `scripts/rag_system.py` (419줄)
- 데이터 삽입: `scripts/insert_to_chroma.py` (118줄)

---

## 다음 단계 (개선 예정)

### Phase 1: Service Layer 구현
- [ ] `services/rag_service.py` 구현
- [ ] `services/chat_service.py` 구현
- [ ] `scripts/rag_system.py` 로직을 Service로 이동

### Phase 2: Database Layer 구현
- [ ] `models/chat.py` SQLModel 정의
- [ ] `repositories/chat_repo.py` CRUD 구현
- [ ] SQLite → PostgreSQL 마이그레이션

### Phase 3: 고도화
- [ ] Redis 캐싱 (세션, 검색 결과)
- [ ] JWT 인증
- [ ] Rate Limiting
- [ ] WebSocket 실시간 채팅

---

**작성일**: 2025-01-19
**최종 수정**: 2025-01-19
