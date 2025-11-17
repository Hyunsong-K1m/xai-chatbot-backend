from fastapi import FastAPI
from app.routers import rag
from app.routers import health
from app.routers import mobile_api #<heo> 모바일 api 라우터 추가

app = FastAPI()

@app.get("/")
def root():
    return {"message": "서버 정상 동작 중"}

app.include_router(rag.router, prefix="/api/v1")


#<heo> 모바일 api 라우터 추가
app.include_router(
    mobile_api.router,
    prefix="",  # prefix는 라우터에서 이미 정의됨
    tags=["Mobile API"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
