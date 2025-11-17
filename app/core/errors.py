#<heo> - 에러 처리 개선
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    """커스텀 API 예외"""
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: dict = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}

# 에러 응답 포맷
def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict = None
) -> JSONResponse:
    """통일된 에러 응답 생성"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {}
            }
        }
    )

# 전역 에러 핸들러
async def api_exception_handler(request: Request, exc: APIException):
    """커스텀 API 예외 처리"""
    logger.error(f"API Error: {exc.error_code} - {exc.message}")
    return create_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 처리"""
    logger.error(f"HTTP Error {exc.status_code}: {exc.detail}")
    return create_error_response(
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}",
        message=str(exc.detail)
    )

async def validation_exception_handler(request: Request, exc):
    """입력 검증 에러 처리"""
    logger.error(f"Validation Error: {exc}")
    return create_error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="입력 데이터 검증 실패",
        details={"errors": exc.errors()}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 처리"""
    logger.error(f"Unexpected Error: {exc}", exc_info=True)
    return create_error_response(
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="서버 내부 오류가 발생했습니다"
    )

# main.py에 추가할 내용
"""
from app.core.error_handlers import (
    APIException,
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from fastapi.exceptions import RequestValidationError

# 에러 핸들러 등록
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
"""