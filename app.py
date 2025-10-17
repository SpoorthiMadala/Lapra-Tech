import streamlit as st
import pandas as pd
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import CTransformers

# ---------------- SETTINGS ----------------
st.set_page_config(page_title="Free Excel Chatbot", page_icon="🤖", layout="wide")
st.title("🧠 Free Excel Knowledge Chatbot (No API Keys!)")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLyLYPptNyIgUvgLLcdjxmLcy8ZbcVL5MJk5o5wMDwBXXZCD5VHj2_9Gj5z-wGBnAuaCkj-iJYezPX/pub?output=csv"

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

def build_vectorstore():
    df = load_data()
    texts = [f"{row}" for row in df.to_dict(orient='records')]
    embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
    vectorstore = Chroma.from_texts(texts, embeddings)
    return vectorstore

st.sidebar.success("✅ Connected to Google Sheet")
vectorstore = build_vectorstore()

# ---------------- LOCAL MODEL ----------------
st.sidebar.subheader("Model: Mistral 7B (Local Free Model)")
llm = CTransformers(
    model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
    model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    config={'max_new_tokens': 256, 'temperature': 0.7}
)

qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever(search_kwargs={"k": 3}))

# ---------------- CHAT INTERFACE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask your question about the sheet...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = qa.run(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

if st.button("🔄 Refresh Knowledge Base"):
    vectorstore = build_vectorstore()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
    st.success("Knowledge base refreshed with latest sheet data!")
