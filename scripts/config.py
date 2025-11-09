import os
from dotenv import load_dotenv

load_dotenv()

JSON_PATH = "/home/xai/fastapi-backend/data/json"
PERSIST_DIRECTORY = "/home/xai/fastapi-backend/data/chroma"
COLLECTION_NAME = "im_bank"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "nlpai-lab/KURE-v1"
MODEL_KWARGS = {"device": "cpu"} 
ENCODE_KWARGS = {"normalize_embeddings": True}
SEARCH_K = 3
