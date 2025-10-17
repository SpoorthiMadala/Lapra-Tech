from transformers import pipeline
import streamlit as st
import pandas as pd

st.title("📊 Google Sheet Chatbot (Free Cloud Model)")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLyLYPptNyIgUvgLLcdjxmLcy8ZbcVL5MJk5o5wMDwBXXZCD5VHj2_9Gj5z-wGBnAuaCkj-iJYezPX/pub?output=csv"
df = pd.read_csv(CSV_URL)
text_data = "\n".join(df.astype(str).apply(" | ".join, axis=1))

qa_pipeline = pipeline("text-generation", model="google/flan-t5-base")

user_input = st.text_input("Ask about your sheet:")
if st.button("Ask"):
    prompt = f"Answer using this data:\n{text_data}\nQuestion: {user_input}"
    answer = qa_pipeline(prompt, max_new_tokens=80)[0]['generated_text']
    st.write(answer)
