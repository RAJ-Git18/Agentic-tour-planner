import streamlit as st
import requests

st.title("💬 Chat with Tour Planner")
userid = 1

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for m in st.session_state.messages:
    # Align user messages to right
    if m["role"] == "user":
        with st.chat_message("user"):
            st.markdown(m["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(m["content"])

# Input box
user_input = st.chat_input("Ask AI")


if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call FastAPI backend
    response = requests.post(
        f"http://127.0.0.1:8000/api/user-{userid}/classify",
        json={"user_query": user_input},
    )

    data = response.json()
    assistant_msg = data.get("response", "No reply from server 😅")

    # Show assistant message on the left
    with st.chat_message("assistant"):
        st.markdown(assistant_msg)

    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
