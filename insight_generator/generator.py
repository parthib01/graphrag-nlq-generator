import requests
import json

# Replace with your valid Gemini API key
GEMINI_API_KEY = "AIzaSyCiity_vZcvn2PF8El9qvuAgd9lsx799c4"

# Choose model: "gemini-1.5-flash" (fast) or "gemini-1.5-pro" (more powerful)
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def generate_insight(user_query, sql_result):
    """
    Generates a natural language insight from SQL results using Gemini API.
    
    Args:
        user_query (str): The original question from the user
        sql_result (list of dicts): The SQL result rows
        
    Returns:
        str: Natural language summary/insight
    """

    result_text = json.dumps(sql_result, indent=2)

    prompt = f"""
You are an assistant that summarizes SQL query results for business users in simple English.

The user asked:
\"{user_query}\"

The SQL query returned the following result:
{result_text}

Write a clear, concise, natural language summary of this result. Be brief but informative.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        
        # Optional: print raw response for debugging
        print("\nRaw Response:\n")
        print(response.text)

        if response.status_code != 200:
            return f"Error from Gemini: {response.text}"

        result = response.json()
        candidates = result.get("candidates", [])

        if candidates:
            generated_text = candidates[0]["content"]["parts"][0]["text"]
            return generated_text.strip()
        else:
            return "Sorry, I couldn't generate a response."

    except Exception as e:
        return f"Error generating insight: {str(e)}"
