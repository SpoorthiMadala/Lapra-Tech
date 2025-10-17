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
@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_data():
    # Read CSV without headers (first row is actual data)
    df = pd.read_csv(CSV_URL, header=None, dtype=str)
    df.columns = ["id", "name", "state", "city", "category", "start_date", "end_date", "url"]
    df = df.dropna(how='all')  # Remove fully empty rows
    df = df.apply(lambda x: x.str.strip().str.lower())  # Clean text
    return df

df = load_data()
st.sidebar.info(f"💾 Loaded {len(df)} tenders from Google Sheet")

# ------------------ SESSION STATE FOR CHAT ------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ------------------ USER INPUT ------------------
user_input = st.chat_input("Ask me about tenders (e.g., 'Tenders in Guntur for Construction between 2025-10-20 and 2025-10-25')")

# ------------------ FILTER FUNCTION ------------------
def find_tenders(query):
    query = query.lower()
    filtered = df.copy()

    # ------------------ CITY FILTER ------------------
    city_matches = df['city'][df['city'].apply(lambda x: x in query)].unique().tolist()
    if city_matches:
        filtered = filtered[filtered['city'].isin(city_matches)]

    # ------------------ STATE FILTER ------------------
    state_matches = df['state'][df['state'].apply(lambda x: x in query)].unique().tolist()
    if state_matches:
        filtered = filtered[filtered['state'].isin(state_matches)]

    # ------------------ CATEGORY FILTER ------------------
    category_matches = df['category'][df['category'].apply(lambda x: x in query)].unique().tolist()
    if category_matches:
        filtered = filtered[filtered['category'].isin(category_matches)]

    # ------------------ START DATE FILTER ------------------
    start_matches = df['start_date'][df['start_date'].apply(lambda x: x in query)].unique().tolist()
    if start_matches:
        filtered = filtered[filtered['start_date'].isin(start_matches)]

    # ------------------ END DATE FILTER ------------------
    end_matches = df['end_date'][df['end_date'].apply(lambda x: x in query)].unique().tolist()
    if end_matches:
        filtered = filtered[filtered['end_date'].isin(end_matches)]

    # ------------------ RESPONSE ------------------
    if filtered.empty:
        return "❌ Sorry, no tenders match your query."

    response = f"✅ I found {len(filtered)} tender(s) matching your query:\n\n"
    for _, row in filtered.iterrows():
        response += (
            f"**{row['name'].title()}** — {row['category'].title()}\n"
            f"📍 {row['city'].title()}, {row['state'].title()}\n"
            f"🗓️ {row['start_date']} → {row['end_date']}\n"
            f"🔗 [View Details]({row['url']})\n\n"
        )
    response += "For detailed information, click the URLs above."
    return response


# ------------------ PROCESS USER QUERY ------------------
if user_input:
    st.session_state["messages"].append({"role": "user", "text": user_input})
    reply = find_tenders(user_input)
    st.session_state["messages"].append({"role": "assistant", "text": reply})

# ------------------ DISPLAY CHAT ------------------
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["text"])
    else:
        st.chat_message("assistant").markdown(msg["text"])

# ------------------ REFRESH BUTTON ------------------
if st.sidebar.button("🔄 Refresh Google Sheet"):
    st.cache_data.clear()  # Clear cached data
    st.sidebar.success("✅ Google Sheet cache cleared! New data will load automatically.")
