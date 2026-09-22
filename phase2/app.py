import uuid

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="CURT Inventory Assistant",
    page_icon="🏎️",
)

st.title("🏎️ CURT Inventory Assistant")
st.caption("Ask about the Formula Student team's inventory.")


# Create a session ID once for this browser session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
user_message = st.chat_input("Ask about the inventory...")

if user_message:
    # Display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    # Send message to FastAPI
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "session_id": st.session_state.session_id,
            "message": user_message,
        },
    )

    if response.ok:
        reply = response.json()["reply"]
    else:
        reply = f"API error: {response.status_code}"

    # Display assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(reply)

with st.sidebar:
    st.title("Inventory")

    if st.button("Refresh Inventory"):
        st.rerun()

    response = requests.get(f"{API_URL}/inventory")

    if response.ok:
        inventory = response.json()

        st.dataframe(
            inventory,
            column_config={
                "id": None,
                "name": "Name",
                "quantity": "Qty",
                "category": "Category",
                "location": "Location",
            },
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.error(
            f"Could not load inventory. API error: {response.status_code}"
        )