import streamlit as st
import pandas as pd

# ------------------ PAGE SETUP ------------------
st.set_page_config(
    page_title="Tender Chatbot",
    page_icon="🤖",
    layout="centered"
)
st.title("🤖 Tender Information Chatbot")

# ------------------ GOOGLE SHEET CSV LINK ------------------
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLyLYPptNyIgUvgLLcdjxmLcy8ZbcVL5MJk5o5wMDwBXXZCD5VHj2_9Gj5z-wGBnAuaCkj-iJYezPX/pub?output=csv"

# ------------------ LOAD DATA ------------------
@st.cache_data(ttl=60)  # cache for 60 seconds
def load_data():
    # Read CSV without headers since first row is actual data
    df = pd.read_csv(CSV_URL, header=None, dtype=str)
    # Assign proper column names
    df.columns = ["id", "name", "state", "city", "category", "start_date", "end_date", "url"]
    # Remove fully empty rows
    df = df.dropna(how='all')
    # Clean text for consistent matching
    df = df.apply(lambda x: x.str.strip().str.lower())
    return df

df = load_data()
st.sidebar.info(f"💾 Loaded {len(df)} tenders from Google Sheet")

# ------------------ SESSION STATE FOR CHAT ------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ------------------ USER INPUT ------------------
user_input = st.chat_input("Ask about tenders (e.g., 'Tenders in Guntur for Construction between 2025-10-20 and 2025-10-25')")

# ------------------ FILTER FUNCTION ------------------
def find_tenders(query):
    query = query.lower()
    filtered = df.copy()

    # Filter by city
    filtered = filtered[filtered['city'].str.contains('|'.join([c for c in df['city'].unique() if c in query]), na=False)]

    # Filter by state
    filtered = filtered[filtered['state'].str.contains('|'.join([s for s in df['state'].unique() if s in query]), na=False)]

    # Filter by category
    filtered = filtered[filtered['category'].str.contains('|'.join([c for c in df['category'].unique() if c in query]), na=False)]

    # Filter by start_date
    filtered = filtered[filtered['start_date'].str.contains('|'.join([d for d in df['start_date'].unique() if d in query]), na=False)]

    # Filter by end_date
    filtered = filtered[filtered['end_date'].str.contains('|'.join([d for d in df['end_date'].unique() if d in query]), na=False)]

    # Generate conversational response
    if filtered.empty:
        return "❌ Sorry, I couldn't find any matching tenders."
    else:
        response = f"✅ I found {len(filtered)} tender(s) matching your query:\n\n"
        for _, row in filtered.iterrows():
            response += (
                f"**{row['name'].title()}** — {row['category'].title()}  \n"
                f"📍 {row['city'].title()}, {row['state'].title()}  \n"
                f"🗓️ {row['start_date']} → {row['end_date']}  \n"
                f"🔗 [View Details]({row['url']})\n\n"
            )
        response += "For detailed information, click the URLs above."
        return response

# ------------------ PROCESS USER QUERY ------------------
if user_input:
    st.session_state["messages"].append({"role": "user", "text": user_input})
    bot_reply = find_tenders(user_input)
    st.session_state["messages"].append({"role": "assistant", "text": bot_reply})

# ------------------ DISPLAY CHAT ------------------
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["text"])
    else:
        st.chat_message("assistant").markdown(msg["text"])

# ------------------ REFRESH BUTTON ------------------
if st.sidebar.button("🔄 Refresh Google Sheet"):
    st.cache_data.clear()
    st.experimental_rerun()
