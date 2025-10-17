import streamlit as st
import pandas as pd
from transformers import pipeline

# ------------------- CONFIG -------------------
st.set_page_config(page_title="Excel Chatbot", page_icon="🤖", layout="centered")
st.title("Lapra-Tech")

# Replace this with your public Google Sheet CSV link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLyLYPptNyIgUvgLLcdjxmLcy8ZbcVL5MJk5o5wMDwBXXZCD5VHj2_9Gj5z-wGBnAuaCkj-iJYezPX/pub?output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

data = load_data()

# Combine all rows into text knowledge
knowledge_text = "\n".join(
    f"Q: {row['Question']} A: {row['Answer']}" for _, row in data.iterrows()
)

# ------------------- MODEL -------------------
st.sidebar.title("🤖 Model Info")
st.sidebar.info("Using free Hugging Face model `google/flan-t5-base`")

# Load model once (free, no key)
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

# ------------------- CHAT SECTION -------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello 👋! I know everything in your Excel sheet. Ask me anything!"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask your question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    prompt = f"""
    You are an assistant. Use the following knowledge base to answer questions accurately.

    Knowledge base:
    {knowledge_text}

    Question: {user_input}
    Answer:
    """
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = qa_pipeline(prompt, max_new_tokens=150)[0]['generated_text']
            st.markdown(result)
    st.session_state.messages.append({"role": "assistant", "content": result})

if st.sidebar.button("🔄 Refresh Excel Data"):
    st.cache_data.clear()
    st.experimental_rerun()
