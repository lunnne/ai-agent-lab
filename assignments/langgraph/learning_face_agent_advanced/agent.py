from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END


class StudyState(TypedDict):
    user_input: str
    topic: str
    request_type: str
    level: str
    plan: List[str]
    quiz: List[str]
    draft_output: str
    improved_output: str
    final_output: str



def analyze_request(state):
    user_input = state["user_input"]

    # 기본값
    topic = user_input
    request_type = "plan"
    level = "beginner"

    # 요청 타입 판단
    if "퀴즈" in user_input:
        request_type = "quiz"

    # 난이도 판단
    if "중급" in user_input:
        level = "intermediate"
    elif "고급" in user_input:
        level = "advanced"

    # 🔥 핵심: topic 정리
    topic = user_input.replace("퀴즈 내줘", "") \
                      .replace("공부 계획 만들어줘", "") \
                      .replace("공부해줘", "") \
                            .strip()
    if not topic:
        topic = "일반 학습 주제"

    return {
        "topic": topic,
        "request_type": request_type,
        "level": level,
    }


def route_request(state: StudyState):
    if state["request_type"] == "quiz":
        return "quiz_node"
    return "study_plan_node"


def study_plan_node(state: StudyState):
    topic = state["topic"]
    level = state["level"]

    if level == "beginner":
        plan = [
            f"{topic}의 기본 개념을 이해한다.",
            f"{topic}의 쉬운 예제를 따라 해본다.",
            f"{topic}의 짧은 연습 문제를 풀어본다.",
        ]
    elif level == "intermediate":
        plan = [
            f"{topic}의 핵심 개념을 빠르게 복습한다.",
            f"{topic}의 실전 예제를 분석한다.",
            f"{topic}의 응용 문제를 직접 풀어본다.",
        ]
    else:
        plan = [
            f"{topic}의 심화 개념을 정리한다.",
            f"{topic}의 복잡한 사례를 분석한다.",
            f"{topic}로 미니 프로젝트를 만든다.",
        ]

    draft_output = f"""
[학습 계획 초안]

주제: {topic}
난이도: {level}

1. {plan[0]}
2. {plan[1]}
3. {plan[2]}
""".strip()

    return {
        "plan": plan,
        "quiz": [],
        "draft_output": draft_output,
    }



def quiz_node(state: StudyState):
    topic = state["topic"]

    if "영어" in topic:
        quiz = [
            "다음 문장에서 틀린 부분을 고치세요: She go to school every day.",
            "현재형과 현재진행형의 차이는 무엇인가요?",
            "I have been to Paris. 이 문장의 시제는 무엇인가요?",
        ]
    elif "파이썬" in topic:
        quiz = [
            "if문에서 elif는 언제 사용하나요?",
            "다음 코드의 출력은 무엇인가요?\nprint(2 > 1 and 3 < 5)",
            "조건문에서 == 와 = 의 차이는 무엇인가요?",
        ]
    else:
        quiz = [
            f"{topic}의 핵심 개념은 무엇인가요?",
            f"{topic}를 사용할 수 있는 예시는 무엇인가요?",
            f"{topic}를 배울 때 주의할 점은 무엇인가요?",
        ]

    draft_output = f"""
[퀴즈 초안]

주제: {topic}
난이도: {state["level"]}

1. {quiz[0]}
2. {quiz[1]}
3. {quiz[2]}
""".strip()

    return {
        "quiz": quiz,
        "plan": [],
        "draft_output": draft_output,
    }


def improve_output(state: StudyState):
    level = state["level"]

    tip = f"""
[추가 학습 팁]

- 현재 추천 학습 레벨: {level}
- 오늘은 너무 길게 하지 말고 20~30분만 집중해보세요.
- 직접 써보거나 말해보는 방식으로 복습하면 더 잘 기억됩니다.
""".strip()

    return {
        "improved_output": tip,
    }


def improve_output(state):
    level = state["level"]

    tip = f"""
[추가 학습 팁]

- 현재 추천 학습 레벨: {level}
- 오늘은 너무 길게 하지 말고 20~30분만 집중해보세요.
- 직접 써보거나 말해보는 방식으로 복습하면 더 잘 기억됩니다.
"""

    return {
        "improved_output": tip
    }


def finalize_response(state: StudyState):
    request_type = state["request_type"]
    plan = state.get("plan", [])
    quiz = state.get("quiz", [])

    if request_type == "quiz":
        quiz_text = "\n".join([f"- {q}" for q in quiz])
        content = f"[퀴즈]\n{quiz_text}\n\n"
    else:
        plan_text = "\n".join([f"- {p}" for p in plan])
        content = f"[학습 계획]\n{plan_text}\n\n"

    final_output = content + state["improved_output"]

    return {
        "final_output": final_output,
    }

def build_graph():
    builder = StateGraph(StudyState)

    builder.add_node("analyze_request", analyze_request)
    builder.add_node("study_plan_node", study_plan_node)
    builder.add_node("quiz_node", quiz_node)
    builder.add_node("improve_output", improve_output)
    builder.add_node("finalize_response", finalize_response)

    builder.add_edge(START, "analyze_request")

    builder.add_conditional_edges(
        "analyze_request",
        route_request,
        {
            "study_plan_node": "study_plan_node",
            "quiz_node": "quiz_node",
        },
    )

    builder.add_edge("study_plan_node", "improve_output")
    builder.add_edge("quiz_node", "improve_output")
    builder.add_edge("improve_output", "finalize_response")
    builder.add_edge("finalize_response", END)

    return builder.compile()


graph = build_graph()