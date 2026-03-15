import asyncio
import os
import streamlit as st
from agents import (
    Agent,
    Runner,
    InputGuardrail,
    OutputGuardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)

# -----------------------------
# 0) Streamlit / API key
# -----------------------------
st.set_page_config(page_title="Restaurant Bot", page_icon="🍽️", layout="centered")
st.title("🍽️ Restaurant Bot")
st.caption("Triage → Menu / Order / Reservation / Complaints Handoff")

# Streamlit Cloud / local secrets 대응
api_key = None
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
elif os.getenv("OPENAI_API_KEY"):
    api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
else:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. Streamlit Cloud의 Secrets에 추가해 주세요.")
    st.stop()


# -----------------------------
# 1) Input Guardrail
# -----------------------------
def restaurant_input_guardrail(ctx, agent, user_input):
    if isinstance(user_input, list):
        last_item = user_input[-1]
        if isinstance(last_item, dict):
            text = str(last_item.get("content", "")).lower()
        else:
            text = str(last_item).lower()
    else:
        text = str(user_input).lower()

    off_topic_keywords = [
        "meaning of life", "politics", "math", "weather", "stock", "bitcoin", "philosophy",
        "이성", "정치", "수학", "날씨", "인생의 의미"
    ]
    bad_words = ["fuck", "shit", "bitch", "개새끼", "씨발", "좆", "병신"]

    if any(word in text for word in off_topic_keywords):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "message": "저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요. 메뉴 확인, 주문, 예약, 불만 접수를 도와드릴 수 있어요 🙂"
            },
        )

    if any(word in text for word in bad_words):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "message": "불편하셨을 수 있지만, 정중한 표현으로 말씀해 주시면 더 잘 도와드릴 수 있어요."
            },
        )

    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info=None,
    )


# -----------------------------
# 2) Output Guardrail
# -----------------------------
def restaurant_output_guardrail(ctx, agent, output):
    text = str(output).lower()

    banned_internal_keywords = [
        "system prompt",
        "internal instruction",
        "hidden instruction",
        "secret recipe",
        "internal policy",
        "developer message",
        "chain of thought",
        "tool schema",
        "our internal notes",
    ]

    rude_phrases = [
        "that's not my problem",
        "i don't care",
        "shut up",
        "stupid",
    ]

    if any(word in text for word in banned_internal_keywords):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"message": "죄송하지만 내부 정보는 안내드릴 수 없습니다."},
        )

    if any(word in text for word in rude_phrases):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"message": "죄송합니다. 보다 정중하고 전문적인 표현으로 다시 안내드리겠습니다."},
        )

    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info=None,
    )


# -----------------------------
# 3) Specialist Agents
# -----------------------------
menu_agent = Agent(
    name="Menu Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are a menu specialist for a restaurant. "
        "Answer questions about menu items, ingredients, vegetarian options, and allergies. "
        "Be clear, friendly, concise, and professional. "
        "Do not invent unavailable menu items."
    ),
    output_guardrails=[OutputGuardrail(guardrail_function=restaurant_output_guardrail)],
)

order_agent = Agent(
    name="Order Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are an order specialist for a restaurant. "
        "Help users place an order, confirm items and quantities, and ask short follow-up questions if needed. "
        "Be practical, professional, and polite."
    ),
    output_guardrails=[OutputGuardrail(guardrail_function=restaurant_output_guardrail)],
)

reservation_agent = Agent(
    name="Reservation Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are a reservation specialist for a restaurant. "
        "Help users make a table reservation. "
        "Ask for number of people, date, and time if missing. "
        "Be warm, clear, and polite."
    ),
    output_guardrails=[OutputGuardrail(guardrail_function=restaurant_output_guardrail)],
)

complaints_agent = Agent(
    name="Complaints Agent",
    model="gpt-4o-mini",
    instructions=(
        "You handle unhappy restaurant customers. "
        "Always acknowledge the customer's frustration, apologize sincerely, "
        "and offer practical solutions such as a refund, a discount, or a manager callback. "
        "If the issue sounds serious or repeated, clearly escalate it to a manager. "
        "Be empathetic, calm, professional, and solution-oriented."
    ),
    output_guardrails=[OutputGuardrail(guardrail_function=restaurant_output_guardrail)],
)

# -----------------------------
# 4) Triage Agent
# -----------------------------
triage_agent = Agent(
    name="Triage Agent",
    model="gpt-4o-mini",
    instructions=(
        "You are the restaurant triage agent. "
        "Figure out what the user wants and hand off to the correct specialist.\n\n"
        "Routing rules:\n"
        "- Questions about menu, ingredients, vegetarian options, allergies -> Menu Agent\n"
        "- Requests to order food -> Order Agent\n"
        "- Requests to book or reserve a table -> Reservation Agent\n"
        "- Complaints about food, staff, service, delays, wrong orders, or bad experiences -> Complaints Agent\n\n"
        "Before handing off, briefly say you are connecting the user to the right specialist."
    ),
    handoffs=[menu_agent, order_agent, reservation_agent, complaints_agent],
    input_guardrails=[
        InputGuardrail(
            guardrail_function=restaurant_input_guardrail,
            run_in_parallel=False,
        )
    ],
    output_guardrails=[OutputGuardrail(guardrail_function=restaurant_output_guardrail)],
)

# -----------------------------
# 5) Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "current_agent" not in st.session_state:
    st.session_state["current_agent"] = "Triage Agent"

if "handoff_log" not in st.session_state:
    st.session_state["handoff_log"] = []


# -----------------------------
# 6) Helper
# -----------------------------
def handoff_message(agent_name: str) -> str | None:
    mapping = {
        "Menu Agent": "메뉴 전문가에게 연결되었습니다.",
        "Order Agent": "주문 담당자에게 연결되었습니다.",
        "Reservation Agent": "예약 담당자에게 연결되었습니다.",
        "Complaints Agent": "불만 처리 담당자에게 연결되었습니다.",
    }
    return mapping.get(agent_name)


def build_agent_input():
    # 실제 세션 메모리를 agent에 전달
    history = []
    for m in st.session_state["messages"]:
        history.append(
            {
                "role": m["role"],
                "content": m["content"],
            }
        )
    return history


# -----------------------------
# 7) Previous Messages UI
# -----------------------------
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        agent_label = m.get("agent")
        if agent_label and m["role"] == "assistant":
            st.markdown(f"**현재 응답 에이전트: {agent_label}**")
        st.markdown(m["content"])


# -----------------------------
# 8) Streamed run
# -----------------------------
async def run_restaurant_bot():
    agent_input = build_agent_input()
    result = Runner.run_streamed(triage_agent, agent_input)

    seen_handoff_agents = set()
    final_agent_name = "Triage Agent"
    status_box = st.empty()

    async for event in result.stream_events():
        if event.type == "agent_updated_stream_event":
            new_agent_name = event.new_agent.name
            final_agent_name = new_agent_name

            if new_agent_name not in seen_handoff_agents:
                seen_handoff_agents.add(new_agent_name)

                if new_agent_name != "Triage Agent":
                    msg = handoff_message(new_agent_name)
                    if msg:
                        status_box.info(msg)
                        st.session_state["handoff_log"].append(msg)

    return result.final_output, final_agent_name


# -----------------------------
# 9) Chat input
# -----------------------------
user_text = st.chat_input("무엇을 도와드릴까요?")

if user_text:
    st.session_state["messages"].append(
        {"role": "user", "content": user_text}
    )

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("적절한 담당자를 찾는 중..."):
            try:
                answer, final_agent = asyncio.run(run_restaurant_bot())
                st.session_state["current_agent"] = final_agent

            except InputGuardrailTripwireTriggered as e:
                final_agent = "Input Guardrail"
                answer = "저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요 🙂"
                if getattr(e, "guardrail_result", None):
                    info = e.guardrail_result.output.output_info
                    if isinstance(info, dict) and "message" in info:
                        answer = info["message"]

            except OutputGuardrailTripwireTriggered as e:
                final_agent = "Output Guardrail"
                answer = "죄송합니다. 안전하고 정중한 방식으로만 안내드릴 수 있어요."
                if getattr(e, "guardrail_result", None):
                    info = e.guardrail_result.output.output_info
                    if isinstance(info, dict) and "message" in info:
                        answer = info["message"]

            except Exception as ex:
                final_agent = "System"
                answer = f"죄송합니다. 요청을 처리하는 중 문제가 발생했습니다. 다시 시도해 주세요.\n\n`{ex}`"

            st.markdown(f"**현재 응답 에이전트: {final_agent}**")
            st.markdown(answer)

    st.session_state["messages"].append(
        {
            "role": "assistant",
            "content": answer,
            "agent": final_agent,
        }
    )