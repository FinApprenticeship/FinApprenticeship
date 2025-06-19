# lan_prompt.py
import streamlit as st

def show():
    st.header("❓ Stelle deine Frage zur Ausbildung")
    st.write("Wir sind hier, um dir zu helfen. Bitte beschreibe deine Frage so genau wie möglich.")

    question = st.text_area("📝 Schreibe deine Frage hier:")

    if st.button("Absenden"):
        if question.strip():
            st.success("🧠 Wird analysiert...")
            # Hier wird später die Weiterleitung zur passenden Seite basierend auf dem LLM-Ergebnis implementiert
        else:
            st.error("⚠️ Bitte gib eine Frage ein, bevor du absendest.")
