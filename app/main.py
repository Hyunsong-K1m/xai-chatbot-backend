from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health
from app.routers import mobile_api #<heo> 모바일 api 라우터 추가

APP_NAME = "finance-qa"
API_PREFIX = "/api/v1"
CORS = ["*"]

app = FastAPI(title=APP_NAME)
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router, prefix=API_PREFIX)


#<heo> 모바일 api 라우터 추가
app.include_router(
    mobile_api.router,
    prefix="",  # prefix는 라우터에서 이미 정의됨
    tags=["Mobile API"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
