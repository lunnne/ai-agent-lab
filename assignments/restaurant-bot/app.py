import asyncio
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
        "Be clear, friendly, and concise."
    ),
)

order_agent = Agent(
    name="Order Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are an order specialist for a restaurant. "
        "Help users place an order, confirm menu items, quantities, and ask follow-up questions if needed. "
        "Be clear and practical."
    ),
)

reservation_agent = Agent(
    name="Reservation Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are a reservation specialist for a restaurant. "
        "Help users make a table reservation. "
        "Ask for number of people, date, and time if missing."
    ),
)

# 2) Triage Agent
triage_agent = Agent(
    name="Triage Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are the restaurant triage agent. "
        "Figure out what the user wants and hand off to the correct specialist.\n\n"
        "Routing rules:\n"
        "- Questions about menu, ingredients, vegetarian options, allergies -> Menu Agent\n"
        "- Requests to order food -> Order Agent\n"
        "- Requests to book or reserve a table -> Reservation Agent\n\n"
        "Before handing off, briefly say you are connecting the user to the right specialist."
    ),
    handoffs=[menu_agent, order_agent, reservation_agent],
)

# 3) UI용 대화 기록
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 4) 이전 메시지 렌더링
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])


def handoff_message(agent_name: str) -> str | None:
    """전문 agent 이름에 따라 UI용 handoff 문구를 반환"""
    mapping = {
        "Menu Agent": "메뉴 전문가에게 연결합니다...",
        "Order Agent": "주문 담당에게 연결합니다...",
        "Reservation Agent": "예약 담당에게 연결합니다...",
    }
    return mapping.get(agent_name)


async def run_restaurant_bot(user_text: str):
    """
    스트리밍 실행:
    - handoff 발생 시 UI에 안내 문구 출력
    - 최종 답변 반환
    """
    result = Runner.run_streamed(triage_agent, user_text)

    seen_handoff_agents = set()

    async for event in result.stream_events():
        # agent가 바뀌는 순간 감지
        if event.type == "agent_updated_stream_event":
            new_agent_name = event.new_agent.name

            # triage -> specialist 로 넘어갈 때만 표시
            if new_agent_name != "Triage Agent" and new_agent_name not in seen_handoff_agents:
                seen_handoff_agents.add(new_agent_name)

                msg = handoff_message(new_agent_name)
                if msg:
                    st.markdown(f"_{msg}_")

    return result.final_output


# 5) 사용자 입력
user_text = st.chat_input("무엇을 도와드릴까요?")

if user_text:
    # user message 저장 + 출력
    st.session_state["messages"].append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # assistant 실행 + 출력
    with st.chat_message("assistant"):
        with st.spinner("적절한 담당자를 찾는 중..."):
            answer = asyncio.run(run_restaurant_bot(user_text))
            st.markdown(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})