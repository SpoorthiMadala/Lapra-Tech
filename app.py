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
    df = pd.read_csv(CSV_URL, dtype=str)  # read all as string
    df = df.dropna(how='all')  # drop completely empty rows
    # Rename columns (your sheet uses A,B,C... headers)
    df.columns = ["id", "name", "state", "city", "category", "start_date", "end_date", "url"]
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
    for city in df['city'].unique():
        if city in query:
            filtered = filtered[filtered['city'] == city]
            break

    # Filter by state
    for state in df['state'].unique():
        if state in query:
            filtered = filtered[filtered['state'] == state]
            break

    # Filter by category
    for cat in df['category'].unique():
        if cat in query:
            filtered = filtered[filtered['category'] == cat]
            break

    # Filter by start_date
    for date in df['start_date'].unique():
        if date in query:
            filtered = filtered[filtered['start_date'] == date]
            break

    # Filter by end_date
    for date in df['end_date'].unique():
        if date in query:
            filtered = filtered[filtered['end_date'] == date]
            break

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
