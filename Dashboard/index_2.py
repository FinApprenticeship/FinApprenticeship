import streamlit as st
import importlib

st.set_page_config(
    page_title="FinApprenticeship Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session init
if "entered_dashboard" not in st.session_state:
    st.session_state.entered_dashboard = False

# ---------------- LANDING PAGE ----------------
if not st.session_state.entered_dashboard:
    st.markdown("""
        <style>
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .start-button {
            margin-top: 2rem;
            padding: 0.8rem 2rem;
            font-size: 1.2rem;
            font-weight: bold;
            background: linear-gradient(90deg, #00ffd0, #00c3ff, #00ff88);
            color: black;
            border: none;
            border-radius: 12px;
            box-shadow: 0 0 15px #00ffd0;
        }
        .start-button:hover {
            background: linear-gradient(90deg, #00ff88, #00c3ff, #00ffd0);
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    st.image("FinApprenticeship_Background.png", use_container_width=True)

    if st.button("▶ Enter Dashboard", key="start_button"):
        st.session_state.entered_dashboard = True
        st.rerun()

    st.text_input("Press ENTER to continue", key="start_trigger", label_visibility="collapsed")
    if st.session_state.start_trigger != "":
        st.session_state.entered_dashboard = True
        st.rerun()

    st.stop()

# ---------------- STYLING ----------------
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #022e2e !important;
        color: #e0fff9;
    }

    header[data-testid="stHeader"] {
        background: linear-gradient(to right, #023535, #005f5f);
        border-bottom: 3px solid #00ffd0;
    }

    section[data-testid="stSidebar"] {
        background: rgba(0, 80, 80, 0.85);
    }

    .stTabs [data-baseweb="tab"] {
        color: #cafffb !important;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(to right, #00ffd0, #00c3ff);
        color: black !important;
        border-radius: 12px;
        box-shadow: 0 0 12px #00ffd0;
    }

    .stButton > button {
        background: linear-gradient(90deg, #00ffd0, #00c3ff);
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 8px;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #00c3ff, #00ffd0);
        color: white;
    }

    /* Radiobutton-MARKER (nur Punkt) in Blau */
    input[type="radio"]:checked + div > div {
        background-color: #00c3ff !important;
        border-color: #00c3ff !important;
    }

    /* Chips (MultiSelect-Tags): NICHT überschreiben → Rot bleibt */

    /* Dropdown-Felder (Select) Türkis gerahmt */
    div[data-baseweb="select"] {
        border-color: #00c3ff !important;
        box-shadow: 0 0 0 2px #00c3ff !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"]:hover {
        border-color: #00e0ff !important;
        box-shadow: 0 0 0 2px #00e0ff !important;
    }

    div[data-baseweb="select"] > div:focus-within {
        border-color: #00ffd0 !important;
        box-shadow: 0 0 0 2px #00ffd0 !important;
    }

    /* Hauptbereich */
    .stMainBlockContainer {
        padding: 3rem 2rem;
        background-color: #022e2e;
        border-radius: 1rem;
        box-shadow: 0 0 30px rgba(0, 255, 208, 0.15);
    }

    /* Logo oben rechts */
    .custom-logo {
        position: fixed;
        top: 0.5rem;
        right: 1rem;
        z-index: 9999;
    }
    </style>
""", unsafe_allow_html=True)

# Logo oben rechts
with st.container():
    st.markdown('<div class="custom-logo">', unsafe_allow_html=True)
    st.image("FinApprenticeship_Background.png", width=90)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MODULE-LOGIK ----------------
PAGES = {
    "Visualisierung": "visualization",
    "Vorhersage": "prediction",
    "Simulation": "simulation",
}

def main():
    tab_labels = list(PAGES.keys())
    tabs = st.tabs(tab_labels)
    for i, tab in enumerate(tabs):
        with tab:
            module_name = PAGES[tab_labels[i]]
            try:
                page_module = importlib.import_module(module_name)
                if hasattr(page_module, "app"):
                    page_module.app()
                else:
                    st.error(f"Modul '{module_name}' hat keine 'app'-Funktion.")
            except ModuleNotFoundError:
                st.error(f"Modul '{module_name}' nicht gefunden.")

st.session_state.entered_dashboard = True

if __name__ == "__main__":
    main()