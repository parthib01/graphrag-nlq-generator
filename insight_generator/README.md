# Insight Generator - Natural Language Summary (M4)

This module generates plain English insights based on the SQL query result and the user's natural language query. It uses an LLM (Gemini) to produce business-friendly summaries from raw SQL outputs.

---

## ✅ Files Included

| File Name            | Description                                                   |
|----------------------|---------------------------------------------------------------|
| `generator.py`       | Core logic to generate natural language insight using LLM     |
| `test_generator.py`  | Simple script to test `generator.py` independently            |
| `requirements.txt`   | Required Python libraries (`requests`, `openai`, etc.)        |

---

## ✅ How to Test Locally

1. **Install dependencies**

```bash
pip install -r requirements.txt


## ✅ Function Overview

The main function provided is:

```python
generate_insight(user_query: str, sql_result: list[dict]) -> str
