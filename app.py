import os
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

# --- TÙY CHỈNH GIAO DIỆN (CSS) ĐẶC SẮC & SINH ĐỘNG ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #f4fbf7, #eef6fc);
    }
    .main-title {
        font-size: 2.5rem;
        color: #0b6623;
        font-weight: 800;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #374151;
        font-weight: 500;
        margin-bottom: 20px;
    }
    [data-testid="stSidebar"] {
        background-color: #f0fdf4;
        border-right: 2px solid #bbf7d0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        border-radius: 10px;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669, #047857);
        box-shadow: 0 6px 8px -1px rgba(16, 185, 129, 0.4);
        color: white;
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
    st.markdown("### 🌿 Cổng Điều Hướng Dữ Liệu")
    st.markdown("---")
    
    input_method = st.radio(
        "**Chọn phương thức nhập liệu:**",
        ("Tải lên file (PDF, DOCX, TXT)", "Nhập văn bản trực tiếp")
    )
    
    project_text = ""
    
    if input_method == "Tải lên file (PDF, DOCX, TXT)":
        uploaded_file = st.file_uploader("Tải tài liệu dự án (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                file_extension = uploaded_file.name.split(".")[-1].lower()
                extracted_text = ""
                if file_extension == "txt":
                    extracted_text = uploaded_file.read().decode("utf-8")
                elif file_extension == "pdf":
                    reader = PdfReader(uploaded_file)
                    max_pages = min(len(reader.pages), 15)
                    for i in range(max_pages):
                        text = reader.pages[i].extract_text()
                        if text:
                            extracted_text += text + "\n"
                elif file_extension == "docx":
                    doc = Document(uploaded_file)
                    for para in doc.paragraphs:
                        extracted_text += para.text + "\n"
                
                project_text = extracted_text[:12000]
                st.success(f"🌱 Đã tối ưu & nạp dữ liệu: **{uploaded_file.name}**")
            except Exception as e:
                st.error(f"❌ Lỗi khi đọc file: {e}")
    else:
        project_text = st.text_area(
            "Nhập mô tả chi tiết dự án:",
            height=250,
            placeholder="Nhập thông tin về quy mô, công nghệ, vị trí, nguyên nhiên liệu..."
        )
    
    st.markdown("---")
    analyze_button = st.button("🚀 Phân Tích Siêu Tốc", use_container_width=True)

# --- MAIN CONTENT: GIAO DIỆN CHÍNH ---
st.markdown('<p class="main-title">🌍 AI Phân Tích Dự Án Môi Trường</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Trợ lý trí tuệ nhân tạo tốc độ cao hỗ trợ <b>Đánh giá Tác động Môi trường & Xã hội (ĐTM-ĐTXH)</b>.</p>', unsafe_allow_html=True)
st.markdown("---")

if analyze_button:
    if not api_key:
        st.error("⚠️ Chưa cấu hình `GEMINI_API_KEY` trong Streamlit Secrets! Vui lòng vào phần Settings -> Secrets trên Streamlit Cloud để thiết lập.")
    elif not project_text.strip():
        st.warning("⚠️ Vui lòng tải lên tài liệu hoặc nhập nội dung mô tả dự án trước khi tiến hành phân tích.")
    else:
        try:
            genai.configure(api_key=api_key)
            # Giữ nguyên model mà bạn đang sử dụng
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            prompt = """
Bạn là một chuyên gia hàng đầu về Đánh giá Tác động Môi trường và Xã hội (ĐTM-ĐTXH). Hãy phân tích nhanh văn bản dự án dưới đây và trả về kết quả bằng tiếng Việt, rõ ràng, chuyên nghiệp theo cấu trúc:

1. Tóm tắt tổng quan dự án
- Tên dự án (nếu có), mục tiêu chính, quy mô, công nghệ áp dụng và vị trí triển khai.

2. Đánh giá tác động môi trường & xã hội (ĐTM - ĐTXH)
- Phân tích chi tiết các tác động tích cực và tiêu cực đối với:
  + Không khí (khí thải, bụi, tiếng ồn, nhiệt độ...)
  + Nguồn nước (nước mặt, nước ngầm, lưu lượng, xử lý nước thải...)
  + Đất đai (sử dụng đất, xói mòn, nguy cơ ô nhiễm đất...)
  + Hệ sinh thái & Đa dạng sinh học (ảnh hưởng đến động thực vật, cảnh quan tự nhiên...)
  + Tác động đến xã hội (đời sống cộng đồng dân cư, việc làm, an sinh xã hội, y tế, văn hóa và hạ tầng khu vực...)

3. Giải pháp & Khuyến nghị phát triển bền vững
- Các giải pháp kỹ thuật và quản lý nhằm giảm thiểu tác động tiêu cực đến môi trường và xã hội.
- Đề xuất cải tiến công nghệ, tiết kiệm năng lượng, áp dụng mô hình kinh tế tuần hoàn hoặc bù đắp sinh thái.

Nội dung dự án:
{project_text}
""".format(project_text=project_text)
            
            with st.spinner("⚡ AI đang tiến hành phân tích siêu tốc, vui lòng đợi trong giây lát..."):
                response = model.generate_content(prompt)
                analysis_result = response.text
            
            st.success("🎉 Phân tích hoàn tất thành công!")
            st.markdown("### 📊 Báo Cáo Đánh Giá Tác Động Môi Trường & Xã Hội")
            
            with st.container(border=True):
                st.markdown(analysis_result)
            
        except Exception as e:
            st.error(f"❌ Đã xảy ra lỗi khi gọi Gemini API hoặc xử lý dữ liệu: {e}")
else:
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        with st.container(border=True):
            st.markdown("### 🤖 Giới thiệu Trợ lý AI")
            st.markdown("""
            * **Năng lực chuyên gia:** Được tích hợp tri thức chuyên sâu về Đánh giá Tác động Môi trường và Xã hội (ĐTM-ĐTXH).
            * **Công nghệ tiên tiến:** Vận hành trên nền tảng Google Gemini API với khả năng đọc hiểu tài liệu kỹ thuật phức tạp và phản hồi siêu tốc.
            """)
            
    with col2:
        with st.container(border=True):
            st.markdown("### 🎯 Tiêu Chí Đánh Giá Mới")
            st.markdown("""
            * **Tổng quan dự án**
            * **ĐTM & Tác động xã hội** (Môi trường sống, cộng đồng dân cư, việc làm)
            * **Giải pháp xanh & Phát triển bền vững**
            """)