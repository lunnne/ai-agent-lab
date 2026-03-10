import streamlit as st
from agents import Agent, Runner

st.set_page_config(page_title="Restaurant Bot", page_icon="🍽️")
st.title("🍽️ Restaurant Bot")

# 1) 전문 Agent들
menu_agent = Agent(
    name="Menu Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are a menu specialist for a restaurant. "
        "Answer questions about menu items, ingredients, vegetarian options, and allergies. "
        "Be clear and helpful."
    ),
)

order_agent = Agent(
    name="Order Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are an order specialist for a restaurant. "
        "Help users place an order, confirm items, and ask follow-up questions if needed."
    ),
)

reservation_agent = Agent(
    name="Reservation Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are a reservation specialist for a restaurant. "
        "Help users book a table and ask for number of people, date, and time."
    ),
)

# 2) 아직은 handoff 없는 triage
triage_agent = Agent(
    name="Triage Agent",
    model="gpt-4o-mini",
     instructions=(
        "You are the restaurant triage agent. "
        "Your job is to understand what the user wants and handoff to the correct agent.\n\n"
        "Use these rules:\n"
        "- Menu questions → Menu Agent\n"
        "- Orders → Order Agent\n"
        "- Reservations → Reservation Agent"
    ),
    handoffs=[menu_agent, order_agent, reservation_agent],
)

# 3) UI 메시지 저장
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 4) 이전 메시지 출력
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 5) 입력
user_text = st.chat_input("무엇을 도와드릴까요?")

if user_text:
    st.session_state["messages"].append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    result = Runner.run_sync(triage_agent, user_text)
    answer = result.final_output

    st.session_state["messages"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)