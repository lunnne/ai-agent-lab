import streamlit as st
import uuid
import os
import tempfile
from openai import OpenAI
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool

st.set_page_config(page_title="Life Coach Agent", page_icon=":heart:")
st.title("Life Coach Agent")

# 1) Streamlit UI 세션 메모리
st.session_state.setdefault("ui_messages", [])
# 2) 에이전트 세션 메모리
st.session_state.setdefault("agent_session_id", f"life_coach_{uuid.uuid4().hex}")
if "agent_session" not in st.session_state:
    st.session_state["agent_session"] = SQLiteSession(st.session_state["agent_session_id"])

# 3) OpenAI client (Vector Store 생성/파일 업로드용)
oa = OpenAI()

# 4) Sidebar: 목표 문서 업로드 → Vector Store에 저장
with st.sidebar:
    st.header("Upload Your Goals")
    uploaded = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

    if st.button("Upload") and uploaded is not None:
         # (A) Vector Store가 없으면 생성
        if "vector_store_id" not in st.session_state:
            vs=oa.vector_stores.create(name="life_coach_goals")
            st.session_state["vector_store_id"] = vs.id
        vector_store_id = st.session_state["vector_store_id"]
         # (B) 파일을 임시로 저장한 뒤 OpenAI Files 업로드
        suffix = f".{uploaded.name.split('.')[-1].lower()}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded.getvalue())
            tmp_file_path = tmp_file.name
            
        with open(tmp_file_path, "rb") as f:
            file_obj = oa.files.create(file=f, purpose="assistants") # 파일 업로드(Assistants/Tools 용도)
        os.remove(tmp_file_path)
        # (C) Vector Store에 파일 “첨부” (이 단계에서 파싱/청킹/임베딩 진행)
        oa.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_obj.id,
        )
        st.success(f"업로드 완료! vector_store_id={vector_store_id}")

        st.divider()
        if "vector_store_id" in st.session_state:
            st.caption(f"current vector_store ={st.session_state['vector_store_id']}")
        else:
            st.caption("no uploedte filed yet")

        if st.button("Clear"):
            st.session_state["ui_messages"] = []
            st.session_state["agent_session_id"]=f"life_coach_{uuid.uuid4().hex}"
            st.session_state["agent_session"] = SQLiteSession(st.session_state["agent_session_id"])
            # vector_store_id는 지우지 않음(문서 인덱싱은 유지)
            st.rerun()

# 5) Tools: WebSearch + FileSearch
tools = [WebSearchTool()]

# 문서가 업로드되어 vector_store_id가 생겼다면, file search tool도 추가
if "vector_store_id" in st.session_state:
    tools.append(FileSearchTool(vector_store_ids=[st.session_state["vector_store_id"]],
            max_num_results=5,
            include_search_results=False,))

# 6) Agent: Life Coach (WebSearch + FileSearch)
agent=Agent(
    name="Life Coach",
    model="gpt-4o-mini",
    instructions=(
        "너는 유저를 따뜻하게 격려하면서도 현실적인 계획을 제안하는 라이프 코치야. 한국어로 답해.\n"
        "\n"
        "중요 규칙:\n"
        "1) 사용자가 목표/일기/진행상황을 물으면, 먼저 파일 검색을 시도해.\n"
        "   - 그때 답변 맨 위에: Coach: [목표 문서 검색]\n"
        "2) 습관/동기부여/자기개발 팁이 필요하면 웹 검색을 시도해.\n"
        "   - 그때 답변 중간 또는 위에: Coach: [웹 검색: \"검색어\"]\n"
        "3) 파일 검색과 웹 검색을 결합해서 개인화된 조언을 만들어.\n"
        "\n"
        "답변 형식:\n"
        "- 공감 1~2문장\n"
        "- 실행 팁 3~6개(번호)\n"
        "- 오늘의 아주 작은 행동 1개\n"
    ),
    tools=tools,)

# 7) UI: 이전 대화 렌더링
for message in st.session_state["ui_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8) 사용자 입력 -> Runner
user_text = st.text_input("Enter your text:")

if user_text:
    st.session_state["ui_messages"].append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = Runner.run_sync(agent, user_text, session=st.session_state["agent_session"])
            answer = result.final_output
            st.write(answer)
            st.markdown(answer)
    st.session_state["ui_messages"].append({"role": "assistant", "content": answer})