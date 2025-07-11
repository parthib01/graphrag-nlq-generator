from generator import generate_insight

# Example user query
#user_query = "Show me the most reviewed product in July."
user_query = "Which region had the highest sales in August?"


# Example SQL result
# sql_result = [
#     {"product_name": "Wireless Headphones", "total_reviews": 150}
# ]
sql_result = [
    {"region": "Mumbai", "total_sales": 58400.00}
]



# Generate insight
insight = generate_insight(user_query, sql_result)

# Print the result
print("\nGenerated Insight:\n")
print(insight)