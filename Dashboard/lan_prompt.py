# lan_prompt.py

import streamlit as st

def show():
    st.header("❓ Ask your question about Apprenticeship")
    st.write("We are here to help. Please describe your question in detail.")

    question = st.text_area("📝 Type your question here:")

    if st.button("Submit"):
        if question.strip():
            st.success("🧠 Analyzing...")
            # here will be implemented redirect to needed page based on result from LLM model
        else:
            st.error("⚠️ Please enter a question before submitting.")
