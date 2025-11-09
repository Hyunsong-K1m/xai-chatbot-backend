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
from config import (
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
prompt = ChatPromptTemplate.from_template(
    """당신은 금융 상품 질의응답 어시스턴트입니다.
제공된 문서를 기반으로 답해주세요.
모르면 "제공된 정보에서는 확인할 수 없습니다."라고 말하세요.

[문서 발췌]
{context}

[질문]
{question}

[답변]"""
)

# --- 5. 문서 포맷 함수 ---
def _format_docs(docs: List[Any]) -> str:
    return "\n\n---\n\n".join(getattr(d, "page_content", "") for d in docs)

# --- 6. RAG 체인 구성 ---
def ask(question: str) -> str:
    # 검색된 문서 가져오기
    docs = retriever.invoke(question)
    context = _format_docs(docs)

    # 프롬프트 채우기
    final_prompt = prompt.format(context=context, question=question)

    # LLM 호출
    response = llm.invoke(final_prompt)

    # 텍스트만 추출
    return response.content if hasattr(response, "content") else str(response)
