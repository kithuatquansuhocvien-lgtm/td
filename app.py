import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document

# Cấu hình giao diện trang Streamlit (Wide mode)
st.set_page_config(
    page_title="AI Phân Tích Dự Án Môi Trường",
    page_icon="🌍",
    layout="wide"
)

# Tùy chỉnh CSS giao diện cho bắt mắt và hiện đại hơn
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        height: 45px;
    }
    .uploaded-file-box {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 6px;
        border-left: 4px solid #10B981;
    }
    </style>
""", unsafe_allow_html=True)

# --- KIỂM TRA API KEY TỪ SECRETS ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = ""

# --- SIDEBAR: KHU VỰC ĐẦU VÀO ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/environment-care.png", width=70)
    st.header("📂 Dữ Liệu Dự Án")
    st.markdown("---")
    
    input_method = st.radio(
        "**Chọn phương thức nhập liệu:**",
        ("Tải lên file (PDF, DOCX, TXT)", "Nhập văn bản trực tiếp")
    )
    
    project_text = ""
    
    if input_method == "Tải lên file (PDF, DOCX, TXT)":
        uploaded_file = st.file_uploader("Tải tài liệu (Khuyến nghị file gọn gàng, súc tích):", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                file_extension = uploaded_file.name.split(".")[-1].lower()
                if file_extension == "txt":
                    project_text = uploaded_file.read().decode("utf-8")
                elif file_extension == "pdf":
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            project_text += text + "\n"
                elif file_extension == "docx":
                    doc = Document(uploaded_file)
                    for para in doc.paragraphs:
                        project_text += para.text + "\n"
                
                st.success(f"Đã đọc file: **{uploaded_file.name}**")
            except Exception as e:
                st.error(f"Lỗi khi đọc file: {e}")
    else:
        project_text = st.text_area(
            "Mô tả chi tiết dự án môi trường:",
            height=250,
            placeholder="Nhập thông tin về quy mô, công nghệ, vị trí, nguyên nhiên liệu..."
        )
    
    st.markdown("---")
    analyze_button = st.button("🚀 Bắt đầu Phân Tích", type="primary")

# --- MAIN CONTENT: HIỂN THỊ