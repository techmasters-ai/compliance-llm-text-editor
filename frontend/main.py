# New Streamlit UI design
import streamlit as st
import requests
import os
import io
import docx
import pandas as pd
import PyPDF2

API_BASE = os.getenv("API_BASE")

st.set_page_config(layout="wide")
st.title("🛡️ Document Compliance Checker")

# --- Session State Initialization ---
for key in [
    "rules", "generated_rules", "rule_edits", "rule_file_content",
    "doc_paragraphs", "doc_file_content", "current_index",
    "violation_result", "suggested_fix", "manual_edit"
]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["violation_result", "suggested_fix", "manual_edit"] else []

# --- Utility: Extract Text ---
def extract_text(file):
    file_type = file.name.split('.')[-1].lower()
    if file_type == "txt":
        return file.read().decode("utf-8")
    elif file_type == "pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif file_type == "csv":
        df = pd.read_csv(file)
        return df.to_string(index=False)
    elif file_type == "docx":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

# --- Sidebar: Upload Compliance Rules ---
st.sidebar.header("📜 Upload Compliance Rule Document")
rule_file = st.sidebar.file_uploader("Upload rules (txt/pdf/csv/docx)", type=["txt", "pdf", "csv", "docx"], key="rule_upload")

if rule_file:
    st.session_state.rule_file_content = extract_text(rule_file)
    if st.sidebar.button("📄 Generate Rules with LLM"):
        response = requests.post(f"{API_BASE}/generate_rules", json={"text": st.session_state.rule_file_content})
        if response.ok:
            st.session_state.generated_rules = response.json()["rules"]
            st.session_state.rule_edits = st.session_state.generated_rules.copy()

# --- Sidebar: Display and Edit Rules ---
if st.session_state.rule_edits:
    st.sidebar.subheader("✏️ Compliance Rules")
    for idx, rule in enumerate(st.session_state.rule_edits):
        st.session_state.rule_edits[idx] = st.sidebar.text_area(f"Rule {idx+1}", value=rule)

# --- Main Area: Upload Document to Check ---
col1, col2 = st.columns([1, 3])
with col1:
    st.header("📁 Upload Document to Check")
    doc_file = st.file_uploader("Upload document (txt/pdf/csv/docx)", type=["txt", "pdf", "csv", "docx"], key="doc_upload")
    if doc_file and st.button("📄 Parse Document"):
        text = extract_text(doc_file)
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        st.session_state.doc_paragraphs = paragraphs
        st.session_state.current_index = 0

# --- Main Area: Paragraph Viewer & Checker ---
with col2:
    if st.session_state.doc_paragraphs:
        idx = st.session_state.current_index
        if idx < len(st.session_state.doc_paragraphs):
            prev = st.session_state.doc_paragraphs[idx - 1] if idx > 0 else ""
            curr = st.session_state.doc_paragraphs[idx]
            next_ = st.session_state.doc_paragraphs[idx + 1] if idx < len(st.session_state.doc_paragraphs) - 1 else ""

            st.subheader(f"📌 Paragraph {idx + 1}/{len(st.session_state.doc_paragraphs)}")
            st.markdown(f"**⬅️ Previous:**\n{prev}")
            st.markdown(f"**🟨 Current:**\n{curr}")
            st.markdown(f"**➡️ Next:**\n{next_}")

            if st.button("🔍 Check Compliance Violations"):
                data = {
                    "paragraph": curr,
                    "preceding": prev,
                    "following": next_,
                    "rules": st.session_state.rule_edits
                }
                res = requests.post(f"{API_BASE}/check_compliance_block", json=data)
                if res.ok:
                    out = res.json()
                    st.session_state.violation_result = out["violation"]
                    st.session_state.suggested_fix = out["suggestion"]
                    st.session_state.manual_edit = st.session_state.suggested_fix

        if st.session_state.violation_result:
            st.subheader("⚠️ Violation Found")
            st.code(st.session_state.violation_result, language="text")

        if st.session_state.suggested_fix:
            st.subheader("✂️ LLM Suggested Fix")
            st.session_state.manual_edit = st.text_area("Modify Fix", value=st.session_state.manual_edit)
            if st.button("✅ Accept & Next"):
                st.session_state.doc_paragraphs[idx] = st.session_state.manual_edit
                st.session_state.current_index += 1
                st.session_state.violation_result = None
                st.session_state.suggested_fix = None
                st.session_state.manual_edit = None

        elif st.session_state.current_index is not None:
            if st.button("⏭️ Skip to Next Paragraph"):
                st.session_state.current_index += 1
                st.session_state.violation_result = None
                st.session_state.suggested_fix = None
                st.session_state.manual_edit = None

    elif st.session_state.doc_file_content:
        st.info("📄 Parsed document but no paragraphs found.")
