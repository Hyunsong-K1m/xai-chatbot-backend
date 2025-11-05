from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
import json
import logging
from urllib.parse import urlencode
import secrets

# 로거 설정
logger = logging.getLogger(__name__)

# API 라우터 생성
router = APIRouter(
    prefix="/api/v1/openbanking",
    tags=["openbanking"],
    responses={404: {"description": "Not found"}},
)

# ========================
# 설정
# ========================

class OpenBankingConfig:
    """오픈뱅킹 API 설정"""
    CLIENT_ID = "d2823e79-9cbe-456f-90b5-83921ebb7596"
    CLIENT_SECRET = "feaa54fe-e1d4-4ca0-9a29-ee28d33da1de"
    
    # API URLs
    BASE_URL = "https://testapi.openbanking.or.kr"  # 테스트 서버
    # BASE_URL = "https://openapi.openbanking.or.kr"  # 운영 서버
    
    # 엔드포인트
    TOKEN_URL = f"{BASE_URL}/oauth/2.0/token"
    AUTHORIZE_URL = f"{BASE_URL}/oauth/2.0/authorize"
    USER_ME_URL = f"{BASE_URL}/v2.0/user/me"
    ACCOUNT_LIST_URL = f"{BASE_URL}/v2.0/account/list"
    BALANCE_URL = f"{BASE_URL}/v2.0/account/balance/fin_num"
    TRANSACTION_URL = f"{BASE_URL}/v2.0/account/transaction_list/fin_num"
    
    # Callback URL (프론트엔드 URL로 변경 필요)
    CALLBACK_URL = "http://localhost:8000/api/v1/openbanking/callback"
    
    # 스코프
    SCOPE = "login inquiry transfer"

config = OpenBankingConfig()

# ========================
# 토큰 저장소 (실제로는 DB 사용)
# ========================

class TokenStore:
    """임시 토큰 저장소"""
    def __init__(self):
        self.tokens = {}  # user_id: token_info
        self.states = {}  # state: user_info
    
    def save_token(self, user_id: str, token_info: dict):
        self.tokens[user_id] = {
            **token_info,
            "created_at": datetime.now().isoformat()
        }
    
    def get_token(self, user_id: str) -> Optional[dict]:
        return self.tokens.get(user_id)
    
    def save_state(self, state: str, user_info: dict):
        self.states[state] = user_info
    
    def get_state(self, state: str) -> Optional[dict]:
        return self.states.pop(state, None)

token_store = TokenStore()

# ========================
# Pydantic 모델
# ========================

class AuthorizeRequest(BaseModel):
    """인증 요청"""
    user_id: str = Field(..., description="사용자 ID")
    
class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    user_seq_no: str

class AccountListRequest(BaseModel):
    """계좌 목록 조회 요청"""
    user_id: str = Field(..., description="사용자 ID")

class BalanceRequest(BaseModel):
    """잔액 조회 요청"""
    user_id: str = Field(..., description="사용자 ID")
    fintech_use_num: str = Field(..., description="핀테크 이용번호")

class TransactionRequest(BaseModel):
    """거래내역 조회 요청"""
    user_id: str = Field(..., description="사용자 ID")
    fintech_use_num: str = Field(..., description="핀테크 이용번호")
    from_date: Optional[str] = Field(None, description="조회 시작일 (YYYYMMDD)")
    to_date: Optional[str] = Field(None, description="조회 종료일 (YYYYMMDD)")

# ========================
# API 엔드포인트
# ========================

@router.get("/health", summary="헬스 체크")
async def health_check():
    """오픈뱅킹 API 연동 상태 확인"""
    return {
        "status": "healthy",
        "service": "OpenBanking API",
        "version": "1.0.0",
        "api_server": config.BASE_URL
    }

@router.post("/authorize", summary="사용자 인증 URL 생성")
async def get_authorization_url(request: AuthorizeRequest):
    """
    오픈뱅킹 사용자 인증 페이지 URL을 생성합니다.
    프론트엔드에서 이 URL로 리다이렉트하여 사용자 인증을 진행합니다.
    """
    try:
        # State 생성 (CSRF 방지)
        state = secrets.token_urlsafe(32)
        token_store.save_state(state, {"user_id": request.user_id})
        
        # 인증 URL 파라미터
        params = {
            "response_type": "code",
            "client_id": config.CLIENT_ID,
            "redirect_uri": config.CALLBACK_URL,
            "scope": config.SCOPE,
            "state": state,
            "auth_type": "0"  # 0: 최초인증, 2: 재인증
        }
        
        auth_url = f"{config.AUTHORIZE_URL}?{urlencode(params)}"
        
        return {
            "success": True,
            "auth_url": auth_url,
            "state": state,
            "message": "사용자를 인증 페이지로 리다이렉트해주세요"
        }
        
    except Exception as e:
        logger.error(f"Authorization URL generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback", summary="인증 콜백 처리")
async def handle_callback(
    code: str = Query(..., description="인증 코드"),
    state: str = Query(..., description="상태값"),
    scope: Optional[str] = Query(None),
):
    """
    오픈뱅킹 인증 후 콜백을 처리합니다.
    인증 코드를 사용하여 액세스 토큰을 발급받습니다.
    """
    try:
        # State 검증
        user_info = token_store.get_state(state)
        if not user_info:
            raise HTTPException(status_code=400, detail="Invalid state")
        
        # 액세스 토큰 요청
        async with httpx.AsyncClient() as client:
            token_params = {
                "code": code,
                "client_id": config.CLIENT_ID,
                "client_secret": config.CLIENT_SECRET,
                "redirect_uri": config.CALLBACK_URL,
                "grant_type": "authorization_code"
            }
            
            response = await client.post(
                config.TOKEN_URL,
                data=token_params
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Token request failed: {response.text}"
                )
            
            token_data = response.json()
            
            # 토큰 저장
            token_store.save_token(user_info["user_id"], token_data)
            
            return {
                "success": True,
                "user_id": user_info["user_id"],
                "message": "인증 성공",
                "token_info": {
                    "expires_in": token_data.get("expires_in"),
                    "scope": token_data.get("scope"),
                    "user_seq_no": token_data.get("user_seq_no")
                }
            }
            
    except Exception as e:
        logger.error(f"Callback handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/account/list", summary="계좌 목록 조회")
async def get_account_list(request: AccountListRequest):
    """
    사용자의 등록된 계좌 목록을 조회합니다.
    """
    try:
        # 토큰 조회
        token_info = token_store.get_token(request.user_id)
        if not token_info:
            raise HTTPException(status_code=401, detail="인증이 필요합니다")
        
        # API 호출
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token_info['access_token']}"
            }
            
            params = {
                "user_seq_no": token_info["user_seq_no"],
                "include_cancel_yn": "N",
                "sort_order": "D"
            }
            
            response = await client.get(
                config.ACCOUNT_LIST_URL,
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Account list request failed: {response.text}"
                )
            
            data = response.json()
            
            return {
                "success": True,
                "res_cnt": data.get("res_cnt", 0),
                "res_list": data.get("res_list", []),
                "message": f"{data.get('res_cnt', 0)}개의 계좌를 조회했습니다"
            }
            
    except Exception as e:
        logger.error(f"Account list retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/account/balance", summary="계좌 잔액 조회")
async def get_account_balance(request: BalanceRequest):
    """
    특정 계좌의 잔액을 조회합니다.
    """
    try:
        # 토큰 조회
        token_info = token_store.get_token(request.user_id)
        if not token_info:
            raise HTTPException(status_code=401, detail="인증이 필요합니다")
        
        # 이용기관 거래번호 생성 (unique)
        bank_tran_id = f"{config.CLIENT_ID}U{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(3)}"
        
        # API 호출
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token_info['access_token']}"
            }
            
            params = {
                "bank_tran_id": bank_tran_id,
                "fintech_use_num": request.fintech_use_num,
                "tran_dtime": datetime.now().strftime("%Y%m%d%H%M%S")
            }
            
            response = await client.get(
                config.BALANCE_URL,
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Balance request failed: {response.text}"
                )
            
            data = response.json()
            
            return {
                "success": True,
                "bank_name": data.get("bank_name"),
                "account_alias": data.get("account_alias"),
                "account_num_masked": data.get("account_num_masked"),
                "balance_amt": data.get("balance_amt"),
                "available_amt": data.get("available_amt"),
                "message": f"잔액: {data.get('balance_amt')}원"
            }
            
    except Exception as e:
        logger.error(f"Balance retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/account/transactions", summary="거래내역 조회")
async def get_transactions(request: TransactionRequest):
    """
    특정 계좌의 거래내역을 조회합니다.
    """
    try:
        # 토큰 조회
        token_info = token_store.get_token(request.user_id)
        if not token_info:
            raise HTTPException(status_code=401, detail="인증이 필요합니다")
        
        # 날짜 기본값 설정
        to_date = request.to_date or datetime.now().strftime("%Y%m%d")
        from_date = request.from_date or (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        # 이용기관 거래번호 생성
        bank_tran_id = f"{config.CLIENT_ID}U{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(3)}"
        
        # API 호출
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token_info['access_token']}"
            }
            
            params = {
                "bank_tran_id": bank_tran_id,
                "fintech_use_num": request.fintech_use_num,
                "inquiry_type": "A",  # A: 전체, I: 입금, O: 출금
                "inquiry_base": "D",  # D: 일자, T: 시간
                "from_date": from_date,
                "to_date": to_date,
                "sort_order": "D",  # D: 내림차순, A: 오름차순
                "tran_dtime": datetime.now().strftime("%Y%m%d%H%M%S")
            }
            
            response = await client.get(
                config.TRANSACTION_URL,
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Transaction request failed: {response.text}"
                )
            
            data = response.json()
            
            return {
                "success": True,
                "bank_name": data.get("bank_name"),
                "res_cnt": data.get("res_cnt", 0),
                "res_list": data.get("res_list", []),
                "message": f"{data.get('res_cnt', 0)}건의 거래내역을 조회했습니다"
            }
            
    except Exception as e:
        logger.error(f"Transaction retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/sample-data", summary="테스트용 샘플 데이터")
async def get_sample_data():
    """
    실제 API 연동 전 테스트용 샘플 데이터를 반환합니다.
    """
    return {
        "success": True,
        "message": "샘플 데이터입니다",
        "account_list": [
            {
                "fintech_use_num": "123456789012345678901234",
                "bank_name": "테스트은행",
                "account_alias": "급여통장",
                "account_num_masked": "123-***-****45",
                "account_holder_name": "홍길동"
            }
        ],
        "balance": {
            "balance_amt": "1234567",
            "available_amt": "1234567"
        },
        "transactions": [
            {
                "tran_date": "20241220",
                "tran_time": "143000",
                "inout_type": "입금",
                "tran_type": "급여",
                "print_content": "12월 급여",
                "tran_amt": "3000000",
                "after_balance_amt": "4234567"
            },
            {
                "tran_date": "20241219",
                "tran_time": "120000",
                "inout_type": "출금",
                "tran_type": "카드",
                "print_content": "카드결제",
                "tran_amt": "50000",
                "after_balance_amt": "1234567"
            }
        ]
    }