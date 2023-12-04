import streamlit as st
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
#read pdf
import PyPDF2
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += " "
        text += page.extract_text()
    return text

file="./48343-2023-Technip Energies France SAS- SAPURA-13042023.pdf"
text=read_pdf(file)
#print(text)
tokenizer = AutoTokenizer.from_pretrained("harshildarji/gbert-legal-ner", use_auth_token="AUTH_TOKEN")
model = AutoModelForTokenClassification.from_pretrained("harshildarji/gbert-legal-ner", use_auth_token="AUTH_TOKEN")

ner = pipeline("ner", model=model, tokenizer=tokenizer)
example = text
results = ner(example)
st.write(results)
