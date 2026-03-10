import streamlit as st

st.set_page_config(page_title="Restaurant Bot", page_icon="🍽️")
st.title("🍽️ Restaurant Bot")

user_text = st.chat_input("무엇을 도와드릴까요?")

if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        st.markdown("안녕하세요! 레스토랑 봇입니다.")