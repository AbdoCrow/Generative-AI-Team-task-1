import sys
import uuid
from pathlib import Path

import requests
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
PHASE1_DIR = ROOT_DIR / "phase1"
if str(PHASE1_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE1_DIR))

from phase1.parser import parse_user_input

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="CURT Inventory Assistant",
    page_icon="🏎️",
)

st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏎️ CURT Inventory Assistant")
st.caption("Ask about the Formula Student team's inventory.")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

tab1, tab2 = st.tabs(["Phase 1", "Phase 2"])

with tab1:
    user_input = st.text_input(
        "Ask about the inventory:",
        placeholder="Ask about the inventory...",
        label_visibility="collapsed",
        key="phase1_input",
    )
    if user_input:
        answer = parse_user_input(user_input)
        st.write(answer)

with tab2:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Ask about the inventory...")
    if user_message:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        with st.chat_message("user"):
            st.markdown(user_message)

        try:
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
        except Exception:
            reply = "Could not connect to FastAPI server."

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

    try:
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
            st.error(f"Could not load inventory. API error: {response.status_code}")
    except Exception:
        st.error("Could not load inventory. FastAPI server is offline.")
