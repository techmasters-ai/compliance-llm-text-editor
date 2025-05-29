import streamlit as st
from frontend.components import uploader

st.set_page_config(page_title="Interactive Editor", layout="wide")
st.markdown("<h1 style='text-align: center;'>Interactive Document Editor</h1>", unsafe_allow_html=True)

project_id = st.sidebar.selectbox("Select Project", [1, 2])
uploader.display(project_id)