# RAG
import os
from typing import List, Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import PERSIST_DIRECTORY, COLLECTION_NAME, OPENAI_API_KEY, MODEL_NAME, MODEL_KWARGS, ENCODE_KWARGS, SEARCH_K

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

retriever = vectorstore.as_retriever(search_type="similarity",
                                     search_kwargs={"k": SEARCH_K})
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    api_key=OPENAI_API_KEY,
)

prompt = ChatPromptTemplate.from_template(
    """당신은 금융 상품 질의응답 어시스턴트입니다.
제공된 문서를 기반으로 답해주세요
모르면 "제공된 정보에서는 확인할 수 없습니다."라고 말하세요.

[문서 발췌]
{context}

[질문]
{question}

[답변]"""
)

def _format_docs(docs: List[Any]) -> str:
    return "\n\n---\n\n".join(getattr(d, "page_content", "") for d in docs)

rag_chain = (
    {
        "context": retriever | _format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

def ask(question: str) -> str:
    return rag_chain.invoke(question)
