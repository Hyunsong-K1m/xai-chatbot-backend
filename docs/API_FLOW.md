# API Flow Diagrams

## 📊 주요 플로우 다이어그램

---

## 1. RAG 질의응답 플로우

```mermaid
sequenceDiagram
    participant U as User/Frontend
    participant R as Router<br/>(rag.py)
    participant RAG as RAG System<br/>(scripts/rag_system.py)
    participant C as ChromaDB
    participant L as LLM<br/>(OpenAI GPT-4o)

    U->>R: POST /api/v1/rag-query<br/>{"question": "높은 금리 예금 추천"}
    R->>RAG: ask(question)

    RAG->>RAG: 질문 전처리<br/>(특수문자 제거)
    RAG->>C: similarity_search(question, k=10)
    C-->>RAG: [상품1, 상품2, ..., 상품10]

    RAG->>RAG: 문서 포맷팅<br/>context = format_docs(docs)
    RAG->>RAG: 프롬프트 생성<br/>prompt + context + question

    RAG->>L: llm.invoke(prompt)
    L-->>RAG: AI 생성 답변

    RAG-->>R: answer
    R-->>U: {"question": "...", "answer": "..."}
```

---

## 2. 오픈뱅킹 인증 플로우

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend<br/>(openbanking_api.py)
    participant OB as OpenBanking<br/>API
    participant TS as TokenStore<br/>(메모리)

    Note over U,TS: 1️⃣ 인증 URL 생성
    F->>B: POST /authorize<br/>{"user_id": "user123"}
    B->>B: state = generate_random()
    B->>TS: save_state(state, user_info)
    B-->>F: {"auth_url": "https://...", "state": "..."}

    Note over U,TS: 2️⃣ 사용자 인증
    F->>U: Redirect to auth_url
    U->>OB: 로그인 및 계좌 선택
    OB->>B: GET /callback?code=xxx&state=yyy

    Note over U,TS: 3️⃣ 토큰 발급
    B->>TS: verify_state(state)
    TS-->>B: user_info
    B->>OB: POST /token<br/>{code, client_id, secret}
    OB-->>B: {access_token, refresh_token}
    B->>TS: save_token(user_id, token_info)
    B-->>F: {"success": true, "message": "인증 성공"}

    Note over U,TS: 4️⃣ 계좌 조회
    F->>B: POST /account/list<br/>{"user_id": "user123"}
    B->>TS: get_token(user_id)
    TS-->>B: access_token
    B->>OB: GET /account/list<br/>Authorization: Bearer {token}
    OB-->>B: {"res_list": [...]}
    B-->>F: 계좌 목록 반환
```

---

## 3. 모바일 채팅 플로우

```mermaid
sequenceDiagram
    participant M as Mobile App
    participant API as mobile_api.py
    participant SM as SessionManager
    participant CS as ChatService<br/>(OpenAI/XAI)

    Note over M,CS: 1️⃣ 세션 생성
    M->>API: POST /session<br/>{"user_id": "user123"}
    API->>SM: create_session(user_id)
    SM-->>API: session_id
    API-->>M: {"session_id": "550e8400-..."}

    Note over M,CS: 2️⃣ 채팅 메시지 전송
    M->>API: POST /chat<br/>{"message": "안녕", "session_id": "..."}
    API->>SM: get_session(session_id)
    SM-->>API: {messages: [...]}

    API->>SM: update_session(user_message)

    API->>CS: process_message(message, context)
    Note right of CS: 시스템 프롬프트 +<br/>이전 대화 5개 +<br/>현재 메시지
    CS->>CS: OpenAI API 호출
    CS-->>API: AI 응답

    API->>SM: update_session(ai_message)
    API-->>M: {"message": {"role": "assistant", "content": "..."}}

    Note over M,CS: 3️⃣ 히스토리 조회
    M->>API: GET /session/{id}/history
    API->>SM: get_session(id)
    SM-->>API: {messages: [...]}
    API-->>M: {"messages": [...], "total_messages": 10}
```

---

## 4. ChromaDB 데이터 삽입 플로우

```mermaid
flowchart TD
    Start([시작: scripts/insert_to_chroma.py]) --> LoadJSON[JSON 파일 로드]

    LoadJSON --> Check{상품목록 키 확인}
    Check -->|있음| Extract1[data = data['상품목록']]
    Check -->|없음| Extract2[data = [data]]

    Extract1 --> Loop[상품별 반복]
    Extract2 --> Loop

    Loop --> Flatten[중첩 딕셔너리<br/>평탄화<br/>flatten_dict]

    Flatten --> Format[텍스트 포맷팅<br/>은행명: ...<br/>상품명: ...<br/>금리: ...]

    Format --> Batch{배치 크기<br/>50개?}
    Batch -->|아니오| Continue[batch.append]
    Batch -->|예| Insert[ChromaDB.add_texts<br/>배치 삽입]

    Continue --> Loop
    Insert --> Loop

    Loop --> Final[남은 데이터 삽입]
    Final --> Complete([완료])

    style Start fill:#e1f5fe
    style Complete fill:#c8e6c9
    style Insert fill:#fff9c4
    style Flatten fill:#f3e5f5
```

---

## 5. 시스템 레이어 아키텍처

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[FastAPI Routers]
        A1[health.py]
        A2[rag.py]
        A3[mobile_api.py]
        A4[openbanking_api.py]
        A --> A1
        A --> A2
        A --> A3
        A --> A4
    end

    subgraph "Business Logic Layer"
        B[Services]
        B1[RAG Service]
        B2[Chat Service]
        B3[OpenBanking Service]
        B --> B1
        B --> B2
        B --> B3
    end

    subgraph "Data Access Layer"
        C[Repositories]
        C1[chat_repo.py]
        C2[doc_repo.py]
        C --> C1
        C --> C2

        D[Vector Store]
        D1[chroma_client.py]
        D --> D1
    end

    subgraph "External Layer"
        E[ChromaDB]
        F[SQLite]
        G[OpenAI API]
        H[OpenBanking API]
    end

    A1 --> B
    A2 --> B1
    A3 --> B2
    A4 --> B3

    B1 --> D1
    B2 --> C1

    C1 --> F
    C2 --> F
    D1 --> E
    B1 --> G
    B2 --> G
    B3 --> H

    style A fill:#bbdefb
    style B fill:#c5e1a5
    style C fill:#fff9c4
    style D fill:#fff9c4
    style E fill:#ffccbc
    style F fill:#ffccbc
    style G fill:#ffccbc
    style H fill:#ffccbc
```

---

## 6. 에러 처리 플로우

```mermaid
flowchart TD
    Request[HTTP Request] --> Router[Router]

    Router --> Try{Try Block}

    Try -->|성공| Response[Success Response<br/>200 OK]

    Try -->|ValidationError| VE[Pydantic 검증 오류]
    Try -->|HTTPException| HE[HTTP 예외]
    Try -->|APIException| AE[커스텀 API 예외]
    Try -->|Exception| GE[일반 예외]

    VE --> Handler1[validation_exception_handler]
    HE --> Handler2[http_exception_handler]
    AE --> Handler3[api_exception_handler]
    GE --> Handler4[general_exception_handler]

    Handler1 --> Error1[422 VALIDATION_ERROR]
    Handler2 --> Error2[4xx/5xx HTTP_XXX]
    Handler3 --> Error3[Custom Error Code]
    Handler4 --> Error4[500 INTERNAL_ERROR]

    Error1 --> Log[로깅]
    Error2 --> Log
    Error3 --> Log
    Error4 --> Log

    Log --> Return[JSON Error Response<br/>{success: false, error: {...}}]

    style Request fill:#e1f5fe
    style Response fill:#c8e6c9
    style Return fill:#ffcdd2
    style Log fill:#fff9c4
```

---

## 7. 데이터 모델 관계도

```mermaid
erDiagram
    ChatSession ||--o{ ChatMessage : contains
    ChatSession {
        string id PK
        string user_id
        datetime created_at
        datetime last_activity
        json metadata
    }

    ChatMessage {
        string id PK
        string session_id FK
        string role
        string content
        datetime timestamp
    }

    FinancialProduct ||--o{ Embedding : has
    FinancialProduct {
        string 은행명
        string 상품명
        string 상품유형
        string 상품설명
        json 금리정보
        json 가입조건
    }

    Embedding {
        string id PK
        string product_id FK
        vector embedding
        string text
        json metadata
    }

    User ||--o{ OpenBankingToken : owns
    User {
        string user_id PK
        string name
    }

    OpenBankingToken {
        string user_id FK
        string access_token
        string refresh_token
        datetime expires_at
        string user_seq_no
    }
```

---

## 8. 배포 아키텍처 (예정)

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Frontend<br/>React/Next.js]
        Mobile[Mobile App<br/>React Native]
    end

    subgraph "Load Balancer"
        LB[Nginx/ALB]
    end

    subgraph "Application Layer"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        API3[FastAPI Instance 3]
    end

    subgraph "Caching Layer"
        Redis[Redis<br/>세션/검색 캐시]
    end

    subgraph "Database Layer"
        Postgres[PostgreSQL<br/>채팅 기록]
        Chroma[ChromaDB<br/>벡터 임베딩]
    end

    subgraph "External Services"
        OpenAI[OpenAI API]
        OpenBanking[오픈뱅킹 API]
    end

    Web --> LB
    Mobile --> LB

    LB --> API1
    LB --> API2
    LB --> API3

    API1 --> Redis
    API2 --> Redis
    API3 --> Redis

    API1 --> Postgres
    API2 --> Postgres
    API3 --> Postgres

    API1 --> Chroma
    API2 --> Chroma
    API3 --> Chroma

    API1 --> OpenAI
    API2 --> OpenBanking

    style Web fill:#e3f2fd
    style Mobile fill:#e3f2fd
    style LB fill:#fff9c4
    style Redis fill:#ffccbc
    style Postgres fill:#c8e6c9
    style Chroma fill:#c8e6c9
    style OpenAI fill:#f3e5f5
    style OpenBanking fill:#f3e5f5
```

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [LangChain 문서](https://python.langchain.com/)
- [ChromaDB 문서](https://docs.trychroma.com/)
- [오픈뱅킹 API 명세](https://openbanking.or.kr/)

**작성일**: 2025-01-19
