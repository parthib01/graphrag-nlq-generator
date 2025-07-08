Step 1: User Enters a Natural Language Question
$ python graphrag_chain.py "Show total sales by category"
This triggers the nlq_pipeline() function.


Step 2: Schema Context is Pulled from Neo4j
Schema Context is Pulled from Neo4j

schema = _get_schema_context()
_get_schema_context() runs Cypher queries on Neo4j to extract:

All table names and columns (Table ➝ HAS_COLUMN ➝ Column)

All foreign key relationships (FOREIGN_KEY edges)

The result is a structured schema description like:


- Product(product_id, category, price, ...)
- Orders(order_id, date, ...)
- FK: Orders.customer_id ➜ Customer.customer_id
This schema is critical to help the LLM not hallucinate.


Step 3: Prompt is Formed for Gemini LLM

prompt = PromptTemplate(...).format(schema=schema, question=user_question)
The LLM gets a prompt like this:

You are an expert database assistant.
Generate ONLY a valid **SQLite** SQL query,
...

Schema:
- Orders(order_id, total_amount, ...)
- Product(category, price, ...)
- FK: OrderItem.product_id ➜ Product.product_id

Question:
Show total sales by category

SQL:

Step 4: Gemini Generates SQL

response = llm.invoke(prompt)
sql = response.content.strip()
Gemini outputs SQL such as:

SELECT category, SUM(total_amount)
FROM Orders
JOIN OrderItem ON Orders.order_id = OrderItem.order_id
JOIN Product ON OrderItem.product_id = Product.product_id
GROUP BY category;


Step 5: SQL is Executed on SQLite

cur = sql_conn.execute(sql)
rows = [dict(r) for r in cur.fetchall()]
The query is executed on the SQLite file (retail.db)
It fetches the data and formats it into JSON-compatible rows

Step 7: Final Output
You see the printed SQL and the resulting rows:

{
  "sql": "SELECT ...",
  "columns": ["category", "total_sales"],
  "rows": [
    {"category": "Beverages", "total_sales": 12345.67},
    {"category": "Snacks", "total_sales": 8901.23}
  ],
  "error": null
}



What Makes This System Smart?
Component	                Purpose
Neo4j Schema Graph	        Prevents hallucination by grounding LLM
LangChain + Gemini	        Converts English to SQL
SQLite	                    Lightweight DB to execute queries
Retry Mechanism	            Fixes minor SQL errors automatically
CLI Interface	            Simple to test and debug