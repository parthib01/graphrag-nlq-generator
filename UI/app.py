import streamlit as st
import requests

# Backend API Endpoint
API_URL = "http://localhost:8000/query"  # Change to your FastAPI URL

# Page Setup
st.set_page_config(page_title="NLQ2SQL Chatbot", layout="centered")
st.title("📊 NLQ to SQL Chatbot")

# Sidebar
with st.sidebar:
    st.header("About")
    st.write(
        "This chatbot uses Gemini."
    )
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.latest_response = None
    st.markdown("---")
    st.write("")


# User Input
with st.form("nlq_form", clear_on_submit=True):
    user_query = st.text_input("Ask a data question:")
    submitted = st.form_submit_button("Submit")

# Submit Query to Backend
if submitted and user_query:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"query": user_query})
            response.raise_for_status()
            result = response.json()

            # Display Outputs
            st.subheader("🧠 Insight")
            st.success(result.get("insight", "No insight generated."))

            st.subheader("💻 Generated SQL")
            st.code(result.get("sql", "-- No SQL generated --"), language="sql")

            st.subheader("📊 Query Result")
            if "result" in result and result["result"]:
                st.dataframe(result["result"])
            else:
                st.info("No data returned.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
