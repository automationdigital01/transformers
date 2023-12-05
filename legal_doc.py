import streamlit as st
from annotated_text import annotated_text
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
#read pdf
import PyPDF2
uploaded_file = st.file_uploader("Choose a file")

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += " "
        text += page.extract_text()
    return text

if uploaded_file and st.button("submit"):
    
    #file="./48343-2023-Technip Energies France SAS- SAPURA-13042023.pdf"
    text=read_pdf(uploaded_file)
    #print(text)
    tokenizer = AutoTokenizer.from_pretrained("harshildarji/gbert-legal-ner", use_auth_token="AUTH_TOKEN")
    model = AutoModelForTokenClassification.from_pretrained("harshildarji/gbert-legal-ner", use_auth_token="AUTH_TOKEN")
    
    ner = pipeline("ner", model=model, tokenizer=tokenizer)
    example = txt
    results = ner(example)
    st.write(results)
    annotated_text(results)
