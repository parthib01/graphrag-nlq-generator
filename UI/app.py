import streamlit as st
import requests

# Backend API URL
API_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="GraphRAG Insight Generator", layout="wide")

st.markdown("<h1 style='font-size: 42px; color: #4CAF50;'>💬 InsightBuddy</h1>", unsafe_allow_html=True)
st.markdown("### GraphRAG-based Natural Language Insight Generator")

# Sidebar
with st.sidebar:
    st.header("About")
    st.write("This is an assistant that summarizes SQL query results for business users in simple English.")
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
    st.markdown("---")

# Initialize chat history in session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input
user_query = st.text_input("💬 Enter your business question:", placeholder="e.g., Show total sales by category")

if st.button("Ask"):
    if user_query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating response..."):
            try:
                res = requests.post(API_URL, json={"question": user_query})
                if res.status_code == 200:
                    data = res.json()

                    # Store in chat history (latest on top)
                    st.session_state.chat_history.insert(0, {
                        "query": user_query,
                        "sql": data.get("sql_query", ""),
                        "insight": data.get("insight", ""),
                        "output": data.get("output", [])
                    })
                else:
                    st.error("❌ Server Error: " + res.text)
            except Exception as e:
                st.error(f"⚠️ Failed to connect to backend: {str(e)}")

st.markdown("---")
st.markdown("")
# Show chat history
for chat in st.session_state.chat_history:
    
    st.markdown(f"**Question:** {chat['query']}")
    #st.markdown(f"**SQL Query:** `{chat['sql']}`")
    st.markdown("**Output Table:**")
    st.dataframe(chat["output"], use_container_width=True)
    st.markdown(f"**Insight:** _{chat['insight']}_")
    st.markdown("---")
