import streamlit as st
import requests

def display(project_id):
    uploaded = st.file_uploader("Upload Document", type=["txt", "pdf"])
    if uploaded:
        response = requests.post("http://backend:8000/documents/upload/", files={"file": uploaded}, data={"project_id": project_id})
        st.success("Document uploaded.")