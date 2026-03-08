import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_teddynote.prompts import load_prompt
from database import get_retriever, init_database
import os

st.set_page_config(page_title="서울 둘레길 챗봇", page_icon="🥾")
st.title("서울 둘레길 안내 챗봇 🥾")

# 사이드바 설정
with st.sidebar:
    st.write("🔧 관리자 메뉴")

    if st.button("DB에 텍스트 데이터 넣기 (최초 1회)"):
        with st.spinner("DB 구축 중..."):
            init_database("data/extracted_text.txt")
        st.success("데이터베이스 구축 완료!")

    clear_btn = st.button("대화 초기화")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


try:
    retriever = get_retriever()

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    prompt = load_prompt("prompts/trail_rag.yaml", encoding="utf-8")
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
except Exception as e:
    chain = None
    st.warning(
        "데이터베이스가 비어있거나 연결되지 않았습니다. 사이드바에서 데이터를 먼저 넣어주세요."
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

if clear_btn:
    st.session_state["messages"] = []

print_messages()

user_input = st.chat_input("둘레길에 대해 궁금한 점을 물어보세요!")

if user_input:
    if chain is None:
        st.error("데이터베이스 구축이 필요합니다. 사이드바 버튼을 눌러주세요.")
    else:
        st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        container = st.empty()
        ai_answer = ""

        try:
            for token in chain.stream(user_input):
                ai_answer += token
                container.markdown(ai_answer)

            add_message("user", user_input)
            add_message("assistant", ai_answer)
        except Exception as e:
            st.error(f"오류가 발생했습니다. DB가 켜져 있는지 확인해주세요!\n{e}")
