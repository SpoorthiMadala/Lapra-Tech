import streamlit as st
import pandas as pd
import re
from transformers import pipeline

st.set_page_config(page_title="Tender Chatbot", page_icon="📄", layout="wide")
st.title("📊 Tender Info Chatbot (Excel-Powered, Free & Public)")

# =================== LOAD DATA ===================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLyLYPptNyIgUvgLLcdjxmLcy8ZbcVL5MJk5o5wMDwBXXZCD5VHj2_9Gj5z-wGBnAuaCkj-iJYezPX/pub?output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [c.strip().lower() for c in df.columns]  # normalize
    return df

data = load_data()

st.sidebar.success("✅ Connected to Tender Sheet")
st.sidebar.write(f"Rows Loaded: {len(data)}")

# =================== MODEL FOR QUERY PARSING ===================
# (lightweight free model from Hugging Face)
nlp = pipeline("text2text-generation", model="google/flan-t5-base")

# =================== HELPER: FILTER FUNCTION ===================
def find_tenders(user_input):
    df = data.copy()
    user_input = user_input.lower()

    # 1️⃣ Try to detect city name from the query
    cities = df['city'].dropna().unique().tolist()
    detected_city = next((c for c in cities if c.lower() in user_input), None)

    # 2️⃣ If a city is found, filter by it
    if detected_city:
        filtered = df[df['city'].str.lower() == detected_city.lower()]
    else:
        # Use model to guess keywords
        response = nlp(f"Extract keywords for tender search: {user_input}", max_new_tokens=50)[0]['generated_text']
        keywords = re.findall(r'\w+', response.lower())
        filtered = df[df.apply(lambda row: any(kw in str(row).lower() for kw in keywords), axis=1)]

    return filtered, detected_city

# =================== CHATBOT INTERFACE ===================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi 👋! Ask me about tenders — for example: *Are there any tenders in Guntur?*"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Type your question about tenders...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching tenders..."):
            results, city = find_tenders(user_query)

            if not results.empty:
                st.success(f"Found {len(results)} tenders" + (f" in {city}" if city else ""))
                st.dataframe(results[['id', 'state', 'name', 'city', 'start_date', 'end_date', 'url']])

                # Pretty list output
                formatted = "\n\n".join([
                    f"**{row['name']}** — {row['city']}  \n🗓️ {row['start_date']} → {row['end_date']}  \n🔗 [View Tender]({row['url']})"
                    for _, row in results.iterrows()
                ])
                st.markdown(formatted)
            else:
                st.warning("No matching tenders found. Try another city or keyword!")

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Found {len(results)} tenders{' in ' + city if city else ''}."
    })

if st.sidebar.button("🔄 Refresh Sheet"):
    st.cache_data.clear()
    st.experimental_rerun()
