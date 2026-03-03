import streamlit as st
import uuid
from agents import Agent, Runner, SQLiteSession, WebSearchTool

st.set_page_config(page_title="Life Coach Agent", page_icon=":heart:")
st.title("Life Coach Agent")

st.session_state.setdefault("ui_messages", [])
st.session_state.setdefault("agent_session_id", f"life_coach_{uuid.uuid4().hex}")
st.session_state.setdefault("agent_session", SQLiteSession(st.session_state["agent_session_id"]))

if "ui_messages" not in st.session_state:
    st.session_state["ui_messages"] = []

if "agent_session_id" not in st.session_state:
    st.session_state["agent_sessio_id"] = f"life_coach_{uuid.uuid4().hex}"

if "agent_session" not in st.session_state:
    st.session_state["agent_session"] = SQLiteSession(st.session_state["agent_session_id"])

web_search_tool = WebSearchTool()

agent = Agent(
    name="Life Coach",
    model="gpt-4o-mini",
    instructions=(
        "너는 유저를 따뜻하게 격려하면서도 현실적으로 행동을 제안하는 라이프 코치야.\n"
        "한국어로 답해.\n"
        "사용자가 동기부여/자기개발/습관 형성 조언을 원하면, 필요할 경우 웹 검색 도구를 사용해.\n"
        "답변 형식은 아래를 지켜:\n"
        "1) 공감/격려 1~2문장\n"
        "2) 실행 가능한 팁 3~6개 (번호 목록)\n"
        "3) 오늘 당장 할 '아주 작은 행동' 1개\n"
        "\n"
        "중요: 사용자가 '웹 검색:'이 보이길 원하니, 검색을 한다면 답변 맨 위에\n"
        "Coach: [웹 검색: \"검색어\"]\n"
        "형식의 한 줄을 반드시 포함해.\n"
        "검색을 안 했으면 그 줄은 쓰지 마."
    ),
    tools=[web_search_tool],
)

for message in st.session_state["ui_messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_text = st.text_input("Enter your text:")

if user_text:
    st.session_state["ui_messages"].append({"role": "user", "content": user_text})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = Runner.run_sync(agent, user_text, session=st.session_state["agent_session"])
            answer = result.final_output
            st.write(answer)
            st.session_state["ui_messages"].append({"role": "assistant", "content": answer})

if st.button("Clear"):
    st.session_state["ui_messages"] = []
    st.session_state["agent_session"].clear()
    st.rerun()
