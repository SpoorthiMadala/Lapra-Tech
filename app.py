import streamlit as st
import pandas as pd
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

st.title("📗 Public Excel Knowledge Chatbot")

# Public Google Sheet CSV URL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLyLYPptNyIgUvgLLcdjxmLcy8ZbcVL5MJk5o5wMDwBXXZCD5VHj2_9Gj5z-wGBnAuaCkj-iJYezPX/pub?output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

def build_vectorstore():
    df = load_data()
    docs = [f"{row}" for row in df.to_dict(orient="records")]
    embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
    return Chroma.from_texts(docs, embeddings)

vectorstore = build_vectorstore()

# LLM (can replace with local model too)
llm = OpenAI(temperature=0.2)
qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

prompt = st.text_input("Ask something:")
if prompt:
    response = qa.run(prompt)
    st.write("🤖", response)

if st.button("🔄 Refresh Knowledge Base"):
    vectorstore = build_vectorstore()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
    st.success("Knowledge base refreshed!")
