
import streamlit as st
import openai
import os
from PyPDF2 import PdfReader
import docx
from docx import Document

# إعدادات الصفحة
st.set_page_config(page_title="مساعد وزارة المالية", page_icon=":office:", layout="centered")

# تنسيق CSS لتوسيط المحتوى وتلوين النص
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    h1, h2, h3, .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #004225 !important;
        text-align: center !important;
    }
    .stApp {
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# واجهة التطبيق
st.markdown('<div class="centered">', unsafe_allow_html=True)
st.title("مساعد وزارة المالية - الحوكمة والمخاطر والالتزام")
st.markdown('</div>', unsafe_allow_html=True)

api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = api_key

task = st.selectbox("اختر نوع المهمة", [
    "مساعد ذكي - أجب عن سؤال",
    "تلخيص مستند"
])

if task == "تلخيص مستند":
    uploaded_file = st.file_uploader("ارفع مستند PDF أو Word", type=["pdf", "docx"])
    if uploaded_file:
        text = ""
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text()
        elif uploaded_file.name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"

        if text:
            with st.spinner("جاري التلخيص..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "لخص هذا المستند بشكل رسمي ومهني:"},
                        {"role": "user", "content": text}
                    ]
                )
                summary = response.choices[0].message["content"]
                st.markdown("### الملخص:")
                st.write(summary)

                docx_file = Document()
                docx_file.add_heading("ملخص المستند", 0)
                docx_file.add_paragraph(summary)
                docx_path = "ملخص_المستند.docx"
                docx_file.save(docx_path)
                with open(docx_path, "rb") as f:
                    st.download_button("تحميل الملخص كـ Word", f, file_name=docx_path)
else:
    user_input = st.text_area("اكتب سؤالك هنا")
    if st.button("إرسال"):
        if user_input:
            with st.spinner("جاري الإجابة..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "أنت مساعد في وزارة المالية، أجب بشكل رسمي ومهني."},
                        {"role": "user", "content": user_input}
                    ]
                )
                st.markdown("### الإجابة:")
                st.write(response.choices[0].message["content"])
