import streamlit as st
import os

def app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_dir, "assets", "background.png")
    st.image(image_path, use_container_width=True)

app()