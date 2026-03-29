# Learning Face

Learning Face is a simple education agent built with LangGraph.

## Purpose
This agent helps learners by analyzing their study request and providing either:
- a study plan
- or a quiz

It also uses a custom tool to provide an additional learning tip.

## Core Features
1. Analyze user study request
2. Generate a study plan or quiz based on the request
3. Provide a learning tip using a custom tool

## Graph Structure

START → analyze_request  
analyze_request → make_study_plan (if user asks for a study plan)  
analyze_request → make_quiz (if user asks for a quiz)  
make_study_plan / make_quiz → add_learning_tip → final_response → END

## Tech Stack
- Python
- LangGraph
- LangChain Core Tools

## Example Inputs
- "파이썬 if문 초보 공부 계획 만들어줘"
- "파이썬 if문 퀴즈 내줘"