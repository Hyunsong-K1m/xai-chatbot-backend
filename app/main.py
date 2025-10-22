from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health

APP_NAME = "finance-qa"
API_PREFIX = "/api/v1"
CORS = ["*"]

app = FastAPI(title=APP_NAME)
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router, prefix=API_PREFIX)
