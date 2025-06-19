import streamlit as st
import os

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
    st.Page("streamlit_scenario.py", title="Simulation"),
]

def main():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ❓ Stelle deine Frage zur Ausbildung")
        question = st.text_area("📝 Deine Frage:")
        if st.button("Absenden"):
            if question.strip():
                st.success("🧠 Wird analysiert...")
            else:
                st.error("⚠️ Bitte gib eine Frage ein.")

    pg = st.navigation(PAGES)
    pg.run()

    st.caption("Made with ❤️ by your Data Science Team FinApprenticeship")

if __name__ == "__main__":
    main()
