import streamlit as st
import importlib

# Set page config
st.set_page_config(
    page_title="Dashboard FinAppretinceship",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    /* Header styles */
    header[data-testid="stHeader"] {
        z-index: 1000;
        background: linear-gradient(to right, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.3));
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    
    /* Navigation bar specific styles */
    .stTabs [data-baseweb="tab-list"] {
        position: fixed;
        top: 1.4rem;
        z-index: 1000;
        padding: 0.5rem 2rem 1.3rem 2rem;
        height: 2.5rem;
        align-items: center;
    }

    /* Tab styles */
    .stTabs [data-baseweb="tab"] {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        margin-bottom: 0.5rem;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #ff4b4b !important;
        font-weight: 600;
    }

    .stMainBlockContainer {
        padding: 5rem 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PAGES = {
    "Visualisierung": "visualization",
    "Vorhersage": "prediction",
    "Simulation": "simulation",
}

def main():
    tab_labels = list(PAGES.keys())
    tabs = st.tabs(tab_labels)
    # Show content for each tab
    for i, tab in enumerate(tabs):
        with tab:
            module_name = PAGES[tab_labels[i]]
            try:
                page_module = importlib.import_module(module_name)
                if hasattr(page_module, "app"):
                    page_module.app()
                else:
                    st.error(f"Module '{module_name}' does not have an 'app' function.")
            except ModuleNotFoundError:
                st.error(f"Page module '{module_name}' not found.")

if __name__ == "__main__":
    main()
