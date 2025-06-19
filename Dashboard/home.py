import streamlit as st
import os

base_dir = os.path.dirname(os.path.abspath(__file__))


def app():
    with st.container():
        st.markdown('<div class="cstom-logo">', unsafe_allow_html=True)
        st.image(os.path.join(base_dir, "FinApprenticeship_Background.png"), width=90)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    # Willkommen bei der FinApprenticeship

    Diese Seite ist noch in Entwicklung.
    """)

app()