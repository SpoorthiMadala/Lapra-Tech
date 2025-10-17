import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Tender Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Tender Chatbot – Ask about tenders or general questions!")

# ------------------ LOAD GOOGLE SHEET ------------------
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLyLYPptNyIgUvgLLcdjxmLcy8ZbcVL5MJk5o5wMDwBXXZCD5VHj2_9Gj5z-wGBnAuaCkj-iJYezPX/pub?output=csv"

@st.cache_data(ttl=300)
def load_tenders():
    df = pd.read_csv(CSV_URL, header=None, dtype=str)
    df.columns = ["id", "name", "state", "city", "category", "start_date", "end_date", "url"]
    df = df.dropna(how='all')
    df = df.apply(lambda x: x.str.strip())
    df['text'] = df.apply(
        lambda row: f"Tender: {row['name']}. Category: {row['category']}. Location: {row['city']}, {row['state']}. Dates: {row['start_date']} → {row['end_date']}. URL: {row['url']}",
        axis=1
    )
    return df

df = load_tenders()
st.sidebar.info(f"💾 Loaded {len(df)} tenders from Google Sheet")

# ------------------ EMBEDDINGS & VECTOR STORE ------------------
@st.cache_data(ttl=300)
def create_vectorstore(texts):
    embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = embed_model.encode(texts, convert_to_numpy=True)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, embeddings, embed_model

index, embeddings, embed_model = create_vectorstore(df['text'].tolist())

# ------------------ RETRIEVE FUNCTION ------------------
def retrieve_tenders(query, top_k=3):
    query_embedding = embed_model.encode([query])
    D, I = index.search(query_embedding, top_k)
    results = [df.iloc[i]['text'] for i in I[0] if i < len(df)]
    return results

# ------------------ LOAD PUBLIC MODEL ------------------
@st.cache_resource(ttl=86400)
def load_model():
    model_name = "TheBloke/Wizard-Vicuna-7B-1.0-HF"  # free HF model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=300)
    return generator

generator = load_model()

# ------------------ CHAT STATE ------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

user_input = st.chat_input("Ask me about tenders or general questions...")

if user_input:
    st.session_state["messages"].append({"role": "user", "text": user_input})

    # Retrieve relevant tender info
    retrieved = retrieve_tenders(user_input, top_k=3)
    context_text = "\n".join(retrieved) if retrieved else ""

    # Build prompt for LLM
    prompt = f"""
You are a helpful assistant. Use the following tender information to answer the question.
If the question is general chat, answer normally.

Tender Information:
{context_text}

Question: {user_input}
Answer:
"""

    answer = generator(prompt)[0]['generated_text']

    st.session_state["messages"].append({"role": "assistant", "text": answer})

# ------------------ DISPLAY CHAT ------------------
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["text"])
    else:
        st.chat_message("assistant").markdown(msg["text"])

# ------------------ REFRESH BUTTON ------------------
if st.sidebar.button("🔄 Refresh Google Sheet"):
    st.cache_data.clear()
    st.sidebar.success("✅ Google Sheet cache cleared! New data will load automatically.")
