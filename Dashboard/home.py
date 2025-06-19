import streamlit as st

def app():
    with st.container():
        st.markdown('<div class="custom-logo">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    # Willkommen bei der FinApprenticeship

    Diese Seite ist noch in Entwicklung.
    """)

app()