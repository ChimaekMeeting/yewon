import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.environ.get("DATABASE_URL")
COLLECTION_NAME = "seoul_trail_docs"


def get_vectorstore():
    embeddings = OpenAIEmbeddings()
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=CONNECTION_STRING,
        use_jsonb=True,
    )


def init_database(txt_path):
    """최초 1회 실행: 텍스트 파일을 읽어서 DB에 벡터 데이터로 저장하는 함수"""
    print("텍스트 문서를 로드하고 임베딩합니다...")

    loader = TextLoader(txt_path, encoding="utf-8")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_documents = text_splitter.split_documents(docs)

    vectorstore = get_vectorstore()
    vectorstore.add_documents(split_documents)
    print("DB 저장 완료!")


def get_retriever():
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": 3})
