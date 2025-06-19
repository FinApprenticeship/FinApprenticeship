import streamlit as st
import importlib

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Set page config
st.set_page_config(
    page_title="Dashboard FinAppretinceship",
    layout="wide",
    initial_sidebar_state="expanded"
)

PAGES = [
    st.Page("home.py", title="Startseite"),
    st.Page("visualization.py", title="Visualisierung"),
    st.Page("prediction.py", title="Vorhersage"),
    st.Page("simulation.py", title="Simulation"),
]

def main():
    pg = st.navigation(PAGES)
    pg.run()

if __name__ == "__main__":
    main()

if st.button("👉 Stell deine Frage"):
    st.session_state.page = "question"

import lan_prompt

if st.session_state.page == "dashboard":
    pass
elif st.session_state.page == "question":
    lan_prompt.show()