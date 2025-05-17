import streamlit as st
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI

# חיבור ל-OpenAI עם מפתח מ-Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# פונקציה לסיכום טקסט בעזרת GPT (תחביר חדש)
def summarize_text(text, style="short"):
    prompt = f"Please summarize the following text in a {style} style:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content

# חילוץ טקסט מקובץ PDF
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return " ".join(page.extract_text() or "" for page in reader.pages)

# חילוץ טקסט מקישור
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"שגיאה בגישה לקישור: {e}"

# ניקוי טקסט
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?;:()\[\]]', '', text)
    return text.strip()

# ממשק Streamlit
st.set_page_config(page_title="מערכת סיכום מסמכים")
st.title("📑 מערכת סיכום מסמכים ושאילת שאלות")

option = st.radio("בחר מקור תוכן:", ["קובץ מקומי", "קישור URL"])
summary_style = st.selectbox("בחר סגנון סיכום:", ["short", "detailed", "bullet points"])

if option == "קובץ מקומי":
    uploaded_file = st.file_uploader("העלה קובץ PDF", type="pdf")
    if uploaded_file:
        raw_text = extract_text_from_pdf(uploaded_file)
        cleaned = clean_text(raw_text)
        with st.spinner("יוצר סיכום..."):
            summary = summarize_text(cleaned, style=summary_style)
        st.subheader("📄 סיכום המסמך:")
        st.write(summary)

if option == "קישור URL":
    url = st.text_input("הזן קישור")
    if url:
        raw_text = extract_text_from_url(url)
        cleaned = clean_text(raw_text)
        with st.spinner("יוצר סיכום..."):
            summary = summarize_text(cleaned, style=summary_style)
        st.subheader("🌐 סיכום הקישור:")
        st.write(summary)
