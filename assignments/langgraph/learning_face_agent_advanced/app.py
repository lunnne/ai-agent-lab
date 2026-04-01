import streamlit as st
from agent import graph

st.set_page_config(page_title="Learning Face Advanced", page_icon="🎓")

st.title("Learning Face Advanced")
st.caption("A learning agent that can generate study plans and quizzes, and improve the output.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! 공부 계획이나 퀴즈를 요청해보세요. 예: '파이썬 if문 초보 공부 계획 만들어줘' 또는 '영어 문법 퀴즈 내줘' 등"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("학습 요청을 입력하세요")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.markdown(user_prompt)

    initial_state = {
            "user_input": user_prompt,
            "topic": "",
            "request_type": "",
            "level": "",
            "draft_output": "",
            "improved_output": "",
            "final_output": "",
        }
    result = graph.invoke(initial_state)
    answer = result["final_output"]

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})