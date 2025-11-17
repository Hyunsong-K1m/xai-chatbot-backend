from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# 로거 설정 (간단한 버전)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API 라우터 생성
router = APIRouter(
    prefix="/api/v1/mobile",
    tags=["mobile"],
    responses={404: {"description": "Not found"}},
)

# ========================
# Pydantic 모델 정의
# ========================

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str = Field(..., description="사용자 메시지", min_length=1, max_length=4000)
    session_id: Optional[str] = Field(None, description="세션 ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 컨텍스트")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "XAI 챗봇에 대해 알려주세요",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "context": {"user_id": "user123"}
            }
        }

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    success: bool = Field(..., description="요청 성공 여부")
    session_id: str = Field(..., description="세션 ID")
    message: Dict[str, Any] = Field(..., description="응답 메시지")
    timestamp: datetime = Field(default_factory=datetime.now)
    
class SessionRequest(BaseModel):
    """세션 생성 요청"""
    user_id: Optional[str] = Field(None, description="사용자 ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SessionResponse(BaseModel):
    """세션 응답"""
    success: bool
    session_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None

# ========================
# 세션 관리 (임시 메모리 저장소)
# ========================

class SessionManager:
    """세션 관리 클래스"""
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """새 세션 생성"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "messages": [],
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "metadata": {}
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """세션 조회"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, message: Dict):
        """세션 업데이트"""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append(message)
            self.sessions[session_id]["last_activity"] = datetime.now()
    
    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# 세션 매니저 인스턴스
session_manager = SessionManager()

# ========================
# 실제 AI 서비스
# ========================

class RealChatService:
    def __init__(self):
        # 환경변수에서 API 키 가져오기
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.xai_key = os.getenv("XAI_API_KEY")
        
        # OpenAI 우선, 없으면 XAI 사용
        if self.openai_key:
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.api_key = self.openai_key
            self.model = "gpt-3.5-turbo"  # 또는 "gpt-4"
        elif self.xai_key:
            self.api_url = "https://api.x.ai/v1/chat/completions"
            self.api_key = self.xai_key
            self.model = "grok-beta"
        else:
            self.api_key = None
            logger.warning("No AI API key found. Using mock responses.")
    
    async def process_message(self, message: str, session_id: str = None, **kwargs):
        """실제 AI API 호출"""
        
        # API 키가 없으면 Mock 응답
        if not self.api_key:
            return f"[Mock] 응답: {message}"
        
        try:
            # 대화 히스토리 가져오기
            session = session_manager.get_session(session_id) if session_id else None
            messages = []
            
            # 시스템 프롬프트
            messages.append({
                "role": "system", 
                "content": "당신은 친절한 AI 비서입니다. 사용자의 질문에 도움이 되는 답변을 제공합니다."
            })
            
            # 이전 대화 컨텍스트 (최근 5개만)
            if session and session.get("messages"):
                for msg in session["messages"][-5:]:
                    if msg.get("role") and msg.get("content"):
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            
            # 현재 메시지 추가
            messages.append({"role": "user", "content": message})
            
            # API 호출
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"AI API Error: {response.status_code} - {response.text}")
                    return "죄송합니다. AI 응답을 생성하는데 문제가 발생했습니다."
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except httpx.TimeoutException:
            logger.error("AI API timeout")
            return "응답 시간이 초과되었습니다. 다시 시도해주세요."
        except Exception as e:
            logger.error(f"AI API Error: {str(e)}")
            return "AI 응답 생성 중 오류가 발생했습니다."

# MockRAGService는 그대로 유지
class MockRAGService:
    """임시 RAG 서비스"""
    async def search(self, query: str, top_k: int = 5):
        return [{"text": f"검색 결과 {i+1}", "score": 0.9-i*0.1} for i in range(min(top_k, 3))]
    
    async def generate_answer(self, query: str, search_results: list):
        return f"RAG 응답: {query}에 대한 답변입니다."

# 서비스 인스턴스 (Mock 대신 Real 사용)
chat_service = RealChatService()  # 변경!
mock_rag_service = MockRAGService()

# ========================
# API 엔드포인트
# ========================

@router.get("/health", summary="헬스 체크")
async def health_check():
    """API 서버 상태 확인"""
    return {
        "status": "healthy",
        "service": "XAI Mobile API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/session", response_model=SessionResponse, summary="새 세션 생성")
async def create_session(request: SessionRequest = Body(...)):
    """새로운 채팅 세션을 생성합니다."""
    try:
        session_id = session_manager.create_session(request.user_id)
        
        if request.metadata:
            session_manager.sessions[session_id]["metadata"] = request.metadata
        
        logger.info(f"New session created: {session_id}")
        
        return SessionResponse(
            success=True,
            session_id=session_id,
            created_at=datetime.now(),
            expires_at=None
        )
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse, summary="채팅 메시지 전송")
async def send_message(request: ChatRequest):
    """채팅 메시지를 전송하고 AI 응답을 받습니다."""
    try:
        # 세션 확인 또는 생성
        session_id = request.session_id
        if not session_id or not session_manager.get_session(session_id):
            session_id = session_manager.create_session()
            logger.info(f"Auto-created session: {session_id}")
        
        # 사용자 메시지 저장
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        }
        session_manager.update_session(session_id, user_message)
        
        # 실제 AI 서비스 사용 (변경!)
        ai_response = await chat_service.process_message(
            message=request.message,
            session_id=session_id  # session_id 추가
        )
        
        # AI 응답 저장
        assistant_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        session_manager.update_session(session_id, assistant_message)
        
        return ChatResponse(
            success=True,
            session_id=session_id,
            message=assistant_message
        )
        
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/history", summary="채팅 히스토리 조회")
async def get_chat_history(session_id: str):
    """특정 세션의 채팅 히스토리를 조회합니다."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    
    return {
        "success": True,
        "session_id": session_id,
        "messages": session["messages"],
        "total_messages": len(session["messages"]),
        "created_at": session["created_at"].isoformat()
    }

@router.delete("/session/{session_id}", summary="세션 삭제")
async def delete_session(session_id: str):
    """세션과 관련된 모든 데이터를 삭제합니다."""
    success = session_manager.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    
    return {
        "success": True,
        "message": f"Session {session_id} deleted successfully"
    }

@router.post("/rag/query", summary="RAG 기반 검색")
async def rag_query(
    query: str = Body(..., embed=True),
    top_k: int = Body(5, embed=True)
):
    """RAG 시스템을 사용하여 문서 기반 답변을 생성합니다."""
    try:
        # Mock RAG 서비스 사용
        results = await mock_rag_service.search(query=query, top_k=top_k)
        answer = await mock_rag_service.generate_answer(query=query, search_results=results)
        
        return {
            "success": True,
            "query": query,
            "answer": answer,
            "sources": results[:3] if results else [],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"RAG query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

