# RAG
import os
from typing import List, Any

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from app.config import (
    PERSIST_DIRECTORY,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    MODEL_NAME,
    MODEL_KWARGS,
    ENCODE_KWARGS,
    SEARCH_K,
)

# --- 1. 임베딩 및 DB 설정 ---
embeddings = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs=MODEL_KWARGS,
    encode_kwargs=ENCODE_KWARGS,
)

vectorstore = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)

# --- 2. Retriever 설정 ---
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": SEARCH_K}
)

# --- 3. LLM 설정 ---
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    api_key=OPENAI_API_KEY,
)

# --- 4. 프롬프트 템플릿 ---
#현송 : 프롬포트 약간 수정
prompt = ChatPromptTemplate.from_template(
    """당신은 금융 상품 질의응답 어시스턴트입니다.
질문과 관련된 정보를 아래 문서에서 찾아 정확히 요약하여 답변하세요.
반드시 문서 내용에 근거해 설명하며, 근거 문서에 있는 숫자나 금리 수치를 인용해 설명하세요.
문서에 내용이 있으면 절대 '확인할 수 없습니다'라고 말하지 마세요.
정말로 문서에 아무 내용도 없을 때만 그렇게 답하세요.

[문서 발췌]
{context}

[질문]
{question}

[답변]"""
)

# --- 5. 문서 포맷 함수 ---
def _format_docs(docs: List[Any]) -> str:
    return "\n\n---\n\n".join(getattr(d, "page_content", "") for d in docs)

## --- 6. RAG 체인 구성 ---
def ask(question: str) -> str:
    # 질문 전처리 (불필요한 특수문자만 제거, 띄어쓰기는 유지)
    clean_question = (
        question.replace(",", "")
        .replace("?", "")
        .replace("!", "")
        .strip()
    )
    print(f"[질문 입력] {question} -> [정제 후] {clean_question}")

    # 검색된 문서 가져오기
    docs = retriever.vectorstore.similarity_search(clean_question, k=10)
    print(f"[검색된 문서 수] {len(docs)}")

    if not docs:
        return "제공된 정보에서는 확인할 수 없습니다."

    context = _format_docs(docs)
    final_prompt = prompt.format(context=context, question=question)

    response = llm.invoke(final_prompt)
    return response.content if hasattr(response, "content") else str(response)
