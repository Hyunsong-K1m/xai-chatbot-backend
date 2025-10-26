# app/main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title=os.getenv("APP_NAME", "app"))

@app.get("/health")
def health():
    return {"status": "ok"}
