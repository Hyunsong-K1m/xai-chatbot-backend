import os
from dotenv import load_dotenv

load_dotenv()

JSON_PATH = r"C:\Users\kkhs0\Desktop\xai-chatbot-backend\data\all_json\거치식예금_통합.json"
PERSIST_DIRECTORY = r"./data/chroma"
COLLECTION_NAME = "im_bank"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL_NAME = "nlpai-lab/KURE-v1"
MODEL_KWARGS = {"device": "cuda"}
ENCODE_KWARGS = {"normalize_embeddings": True}

SEARCH_K = 3
