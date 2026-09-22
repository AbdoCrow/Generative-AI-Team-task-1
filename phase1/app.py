import streamlit as st
from parser import parse_user_input

st.title("CURT Inventory Assistant")

user_input = st.text_input("Ask about the inventory:")

if user_input:
    answer = parse_user_input(user_input)
    st.write(answer)