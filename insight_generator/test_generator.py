from generator import generate_insight

# Example user query
user_query = "Show me the most reviewed product in July."

# Example SQL result
sql_result = [
    {"product_name": "Wireless Headphones", "total_reviews": 150}
]



# Generate insight
insight = generate_insight(user_query, sql_result)

# Print the result
print("\nGenerated Insight:\n")
print(insight)