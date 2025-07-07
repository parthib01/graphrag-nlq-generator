import streamlit as st
import requests

# Backend API Endpoint
API_URL = "http://localhost:8000/query"

# Initialize session state for chat history 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Page Setup
st.set_page_config(page_title="NLQ2SQL Chatbot", layout="centered")
st.title("📊 NLQ to SQL Chatbot")

# Sidebar
with st.sidebar:
    st.header("About")
    st.write("This chatbot uses Gemini.")
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
    st.markdown("---")

# User Input Form
with st.form("nlq_form", clear_on_submit=True):
    user_query = st.text_input("Type your question here:", placeholder="e.g., What was the total sales last year?")
    submitted = st.form_submit_button("Ask")

# Submit Query to Backend and get response
if submitted and user_query:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"query": user_query})
            response.raise_for_status()
            result = response.json()
            bot_reply = result.get("insight", "No insight generated")
        except Exception as e:
            bot_reply = f"❌ Error: {str(e)}"
    
    # Insert latest message at the top            
    st.session_state.chat_history.insert(0, {
        "user": user_query,
        "bot": bot_reply
    })

# Display chat history (latest on top)
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(chat["user"])
    with st.chat_message("assistant"):
        st.markdown(chat["bot"])
