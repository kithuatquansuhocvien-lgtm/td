import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document

# Cấu hình giao diện trang Streamlit
st.set_page_config(
    page_title="AI Phân Tích Dự Án Môi Trường",
    page_icon="🌍",
    layout="wide"
)

# Tiêu đề ứng dụng
st.title("🌍 AI Phân Tích Dự Án Môi Trường")
st.markdown("Ứng dụng sử dụng trí tuệ nhân tạo **Google Gemini** để phân tích, đánh giá tác động môi trường (ĐTM) và đề xuất các giải pháp phát triển bền vững cho dự án.")

# --- KIỂM TRA API KEY TỪ SECRETS ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = ""

# --- SIDEBAR: NHẬP LIỆU DỰ ÁN ---
st.sidebar.header("📂 Dữ liệu dự án")

input_method = st.sidebar.radio(
    "Chọn cách cung cấp thông tin dự án:",
    ("Tải lên file (PDF, DOCX, TXT)", "Nhập văn bản trực tiếp")
)

project_text = ""

if input_method == "Tải lên file (PDF, DOCX, TXT)":
    uploaded_file = st.sidebar.file_uploader("Tải lên tài liệu dự án", type=["pdf", "docx", "txt"])
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
            st.sidebar.success(f"Đã đọc thành công file: {uploaded_file.name}")
        except Exception as e:
            st.sidebar.error(f"Lỗi khi đọc file: {e}")
else:
    project_text = st.sidebar.text_area(
        "Nhập mô tả chi tiết dự án môi trường:",
        height=220,
        placeholder="Nhập thông tin về quy mô, công nghệ sử dụng, vị trí, nguyên nhiên liệu, nguồn vốn và các hạng mục hoạt động..."
    )

# Nút phân tích
analyze_button = st.sidebar.button("🔍 Phân tích dự án", type="primary")

# --- MAIN CONTENT: XỬ LÝ & HIỂN THỊ KẾT QUẢ ---
if analyze_button:
    if not api_key:
        st.error("⚠️ Chưa cấu hình `GEMINI_API_KEY` trong Streamlit Secrets! Vui lòng vào phần Settings -> Secrets trên Streamlit Cloud để thiết lập.")
    elif not project_text.strip():
        st.warning("⚠️ Vui lòng tải lên tài liệu hoặc nhập nội dung mô tả dự án trước khi tiến hành phân tích.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # Sử dụng model chuẩn tương thích mới nhất
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            prompt = f"""
Bạn là một chuyên gia hàng đầu về Đánh giá Tác động Môi trường (ĐTM) và Phát triển Bền vững. 
Hãy phân tích tài liệu/văn bản mô tả dự án dưới đây và trả về kết quả bằng tiếng Việt, được định dạng rõ ràng, chuyên nghiệp theo cấu trúc sau:

1. Tóm tắt tổng quan dự án
- Tên dự án (nếu có), mục tiêu chính, quy mô, công nghệ áp dụng và vị trí triển khai.

2. Đánh giá tác động môi trường (ĐTM)
- Phân tích chi tiết các tác động tích cực và tiêu cực đối với:
  + Không khí (khí thải, bụi, tiếng ồn, nhiệt độ...)
  + Nguồn nước (nước mặt, nước ngầm, lưu lượng, xử lý nước thải...)
  + Đất đai (sử dụng đất, xói mòn, nguy cơ ô nhiễm đất...)
  + Hệ sinh thái & Đa dạng sinh học (ảnh hưởng đến động thực vật, cảnh quan tự nhiên...)

3. Giải pháp & Khuyến nghị phát triển bền vững
- Các giải pháp kỹ thuật và quản lý nhằm giảm thiểu tác động tiêu cực.
- Đề xuất cải tiến công nghệ, tiết kiệm năng lượng, áp dụng mô hình kinh tế tuần hoàn hoặc bù đắp sinh thái.

4. Điểm số thân thiện môi trường (Sustainability Score)
- Đánh giá theo thang điểm từ 1 đến 10 (1 là cực kỳ gây hại, 10 là cực kỳ thân thiện/xanh và bền vững).
- Giải thích chi tiết lý do và cơ sở đưa ra mức điểm này.

Nội dung dự án cần phân tích:
{project_text}
"""
            
            with st.spinner("🤖 AI đang tiến hành phân tích ĐTM và đánh giá dự án, vui lòng chờ trong giây lát..."):
                response = model.generate_content(prompt)
                analysis_result = response.text
            
            st.success("✅ Phân tích hoàn tất thành công!")
            st.divider()
            st.markdown("### 📊 Kết Quả Phân Tích Dự Án Môi Trường")
            st.markdown(analysis_result)
            
        except Exception as e:
            st.error(f"❌ Đã xảy ra lỗi khi gọi Gemini API hoặc xử lý dữ liệu: {e}")
else:
    st.info("👈 Hãy cung cấp thông tin dự án ở thanh bên trái (Sidebar), sau đó nhấn nút **'Phân tích dự án'** để bắt đầu.")