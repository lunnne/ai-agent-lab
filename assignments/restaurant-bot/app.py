import streamlit as st
from agents import Agent, Runner

st.set_page_config(page_title="Restaurant Bot", page_icon="🍽️")
st.title("🍽️ Restaurant Bot")

# 1️⃣ Triage Agent (아직 handoff 없음)
triage_agent = Agent(
    name="Triage Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are the restaurant triage agent. "
        "Your job is to understand what the user wants. "
        "Possible topics: menu questions, placing an order, or making a reservation."
    )
)

# 2️⃣ 채팅 기록 UI용 메모리
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 3️⃣ 이전 메시지 다시 그리기
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 4️⃣ 사용자 입력
user_text = st.chat_input("무엇을 도와드릴까요?")

if user_text:
    # user message
    st.session_state["messages"].append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # Agent 실행
    result = Runner.run_sync(triage_agent, user_text)
    answer = result.final_output

    # assistant message
    st.session_state["messages"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)