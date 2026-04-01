# Learning Face Advanced

Learning Face Advanced is an education agent built with LangGraph and Streamlit.

## Overview
This agent helps users with learning by analyzing their request and generating either:
- a study plan
- or a quiz

Then it improves the generated result by adding extra learning tips.

## Advanced Pattern Used
Workflow Architecture - Prompt Chaining

The agent follows a chained workflow:
1. Analyze user study request
2. Generate a study plan or quiz based on the request
3. Improve the output
4. Return the final response

## Graph Structure
START
→ analyze_request
→ conditional routing
   - study_plan_node
   - quiz_node
→ improve_output
→ finalize_response
→ END

## Features
- Multiple LangGraph nodes
- Conditional edge based on user input
- Streamlit chat UI
- End-to-end working education agent

## Example Inputs
- 파이썬 if문 초보 공부 계획 만들어줘
- 영어 문법 퀴즈 내줘
- 자바스크립트 중급 공부 계획 만들어줘

## Run

```bash
uv add langgraph langchain-core streamlit
uv run streamlit run app.py