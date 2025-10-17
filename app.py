import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tender Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Tender Information Chatbot")

# Google Sheet CSV link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLyLYPptNyIgUvgLLcdjxmLcy8ZbcVL5MJk5o5wMDwBXXZCD5VHj2_9Gj5z-wGBnAuaCkj-iJYezPX/pub?output=csv"

# Load the live data
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = ["id", "name", "state", "city", "category", "start_date", "end_date", "url"]
    df = df.astype(str).apply(lambda x: x.str.strip().str.lower())
    return df

df = load_data()

st.info("💡 Data auto-refreshes from Google Sheets every minute.")

# Chat interface
if "messages" not in st.session_state:
    st.session_state["messages"] = []

user_input = st.chat_input("Ask something like 'Are there any tenders in Guntur?'")

def find_tenders(query):
    query = query.lower()
    filtered_df = df.copy()

    # Filter dynamically
    for col in ["city", "state", "category"]:
        for val in df[col].unique():
            if val in query:
                filtered_df = filtered_df[filtered_df[col] == val]
                break

    for date in df['start_date'].unique():
        if date in query:
            filtered_df = filtered_df[filtered_df['start_date'] == date]
            break

    for date in df['end_date'].unique():
        if date in query:
            filtered_df = filtered_df[filtered_df['end_date'] == date]
            break

    return filtered_df

if user_input:
    st.session_state["messages"].append({"role": "user", "text": user_input})

    results = find_tenders(user_input)
    if results.empty:
        bot_response = "Sorry, I couldn't find any matching tenders."
    else:
        bot_response = f"I found {len(results)} tenders:\n\n"
        for _, row in results.iterrows():
            bot_response += (
                f"**{row['name'].title()}**\n"
                f"📍 {row['city'].title()}, {row['state'].title()}\n"
                f"🏷️ {row['category'].title()}\n"
                f"🗓️ {row['start_date']} → {row['end_date']}\n"
                f"🔗 [View Details]({row['url']})\n\n"
            )

    st.session_state["messages"].append({"role": "bot", "text": bot_response})

# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["text"])
    else:
        st.chat_message("assistant").markdown(msg["text"])
