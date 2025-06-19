import streamlit as st
import importlib

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
