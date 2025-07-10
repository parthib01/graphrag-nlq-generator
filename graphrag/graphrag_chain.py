"""
GraphRAG Chain – Gemini Version  (with token / latency metrics)
Author: M3
"""

'''
import os, sqlite3, json, sys, time
from typing import Dict, List
from dotenv import load_dotenv

# ---------------- Config -----------------------------------------------------
USE_FILTERED_SCHEMA = True   # ← flip to False for “full schema” baseline
FUZZY_THRESHOLD     = 60     # partial‑ratio %  for table‑name match

# 0. Load env vars ------------------------------------------------------------
load_dotenv()

# 1. LangChain‑Gemini ---------------------------------------------------------
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# 2. Neo4j --------------------------------------------------------------------
from py2neo import Graph as NeoGraph

# 3. Prompt utils -------------------------------------------------------------
from langchain.prompts import PromptTemplate
from fuzzywuzzy import fuzz
import tiktoken                       # token counting lib

# 4. ENV constants ------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or sys.exit("Missing GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PW   = os.getenv("NEO4J_PASSWORD", "Parthib@0103")
SQLITE_PATH= os.getenv("SQLITE_PATH", "db/retail.db")

# 5. Instantiate resources ----------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.0,
)
neo       = NeoGraph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PW))
# sql_conn  = sqlite3.connect(SQLITE_PATH)
sql_conn  = sqlite3.connect("../db/retail.db")
sql_conn.row_factory = sqlite3.Row

tok = tiktoken.encoding_for_model("gpt-4o-mini")   # any OpenAI‑compatible enc

# 6. Schema retrieval ---------------------------------------------------------
TABLES = ["Customer","OrderItem","Orders","Product","Store","Supplier","Review", "Payment", "Shipment", "Inventory", "Promotion", "ProductPromotion", "Loyalty"]

'''
# def _get_relevant_tables(question: str) -> List[str]:
#     if not USE_FILTERED_SCHEMA:           # full mode
#         return TABLES
#     hits = [tbl for tbl in TABLES
#             if fuzz.partial_ratio(tbl.lower(), question.lower()) >= FUZZY_THRESHOLD]
#     return hits if hits else TABLES       # fallback to full
'''

def _get_relevant_tables(question: str) -> List[str]:
    if not USE_FILTERED_SCHEMA:
        return TABLES

    hits = [tbl for tbl in TABLES if fuzz.partial_ratio(tbl.lower(), question.lower()) >= FUZZY_THRESHOLD]

    if any(word in question.lower() for word in ["sold", "units", "quantity", "order"]):
        for must_have in ["OrderItem", "Orders"]:
            if must_have not in hits:
                hits.append(must_have)
    return hits if hits else TABLES

    q = question.lower()

    # Heuristic boosting
    if any(word in q for word in ["point", "loyalty", "tier"]):
        hits.append("Loyalty")
    if any(word in q for word in ["spend", "total_amount", "order", "purchase"]):
        hits.extend(["Orders", "OrderItem", "Payment"])
    if any(word in q for word in ["shipment", "delivered", "courier", "tracking"]):
        hits.append("Shipment")
    if any(word in q for word in ["review", "rating", "feedback"]):
        hits.append("Review")
    if any(word in q for word in ["inventory", "stock", "quantity"]):
        hits.append("Inventory")
    if any(word in q for word in ["promotion", "discount"]):
        hits.extend(["Promotion", "ProductPromotion"])
    if "returned" in q or "refund" in q:
        hits.extend(["Shipment", "OrderItem", "Product"])
    if "courier" in q or "delivery time" in q:
        hits.append("Shipment")
    if "category" in q:
        hits.append("Product")
    if "brand" in q:
        hits.append("Product")
    if "supplier" in q:
        hits.extend(["Supplier", "Product"])

    # Remove duplicates
    return list(set(hits)) if hits else TABLES

def _get_schema_context(question: str) -> str:
    relevant = _get_relevant_tables(question)
    print(f"[DEBUG] Tables sent to Gemini: {relevant}")
    # Tables + columns
    rows = neo.run("""
        MATCH (t:Table)-[:HAS_COLUMN]->(c:Column)
        WHERE t.name IN $tables
        RETURN t.name AS table, collect(c.name) AS cols
    """, parameters={"tables": relevant}).data()
    lines = [f"- {r['table']}({', '.join(sorted(r['cols']))})" for r in rows]
    # Foreign keys
    fk_rows = neo.run("""
        MATCH (from:Column)-[:FOREIGN_KEY]->(to:Column)
        MATCH (ft:Table)-[:HAS_COLUMN]->(from)
        MATCH (tt:Table)-[:HAS_COLUMN]->(to)
        WHERE ft.name IN $tables AND tt.name IN $tables
        RETURN ft.name AS ft, from.name AS fc, tt.name AS tt, to.name AS tc
    """, parameters={"tables": relevant}).data()
    for r in fk_rows:
        lines.append(f"- FK: {r['ft']}.{r['fc']} ➜ {r['tt']}.{r['tc']}")
    return "\n".join(lines)

PROMPT_TMPL = """
You are an expert SQLite assistant. Use only the tables/columns listed.

Schema:
{schema}

Question:
{question}

Write the SQL only:
"""

SCHEMA_PROMPT = """
You are an expert database assistant.
Generate ONLY a valid **SQLite** SQL query,
using exactly the tables & columns provided.
Avoid extra keywords (e.g., PostgreSQL, MySQL) and do not wrap the query in back‑ticks.

Schema:
{schema}

Question:
{question}

SQL:
"""

# 7. NLQ ➜ SQL ---------------------------------------------------------------
def nlq_to_sql(question: str, retry: bool = True) -> str:
    prompt = PromptTemplate(
        template=SCHEMA_PROMPT, input_variables=["schema", "question"]
    ).format(schema=_get_schema_context(question), question=question)

    print(prompt)
    token_count = len(tok.encode(prompt))
    t0 = time.time()

    response = llm.invoke(prompt)

    latency = time.time() - t0
    USE_FILTERED_SCHEMA = os.getenv("USE_FILTERED_SCHEMA", "true").lower() == "true"
    print(f"[Metrics] tokens={token_count} | LLM latency={latency:.2f}s | filtered={USE_FILTERED_SCHEMA}")
    
    sql = response.content.strip()



    # Remove accidental markdown fences if any
    if sql.startswith("```"):
        sql = sql.split("```")[1].strip()

    # Ensure it's a SELECT query
    if not sql.lower().strip().startswith("select"):
        raise ValueError(f"❌ Invalid SQL generated:\n{sql}")

    return sql


# 8. Execute SQL with one retry ----------------------------------------------
def run_sql(sql: str, question: str, _retry=False) -> Dict:
    try:
        cur = sql_conn.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        cols = [d[0] for d in cur.description]
        return {"sql": sql, "columns": cols, "rows": rows, "error": None}
    except sqlite3.OperationalError as e:
        if not _retry and "syntax" in str(e).lower():
            fix_prompt = f"Error:\n{e}\nFix SQL only:"
            fixed = llm.invoke(fix_prompt).content.strip()
            if fixed.startswith("```"):
                fixed = fixed.split("```")[1].strip()
            return run_sql(fixed, question, _retry=True)
        return {"sql": sql, "columns": [], "rows": [], "error": str(e)}

# 9. Pipeline -----------------------------------------------------------------
def nlq_pipeline(q: str) -> Dict:
    sql = nlq_to_sql(q)
    print("\n🔍  SQL:\n", sql)
    return run_sql(sql, q)

# 10. CLI ---------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python graphrag_chain.py \"<question>\"")
    res = nlq_pipeline(sys.argv[1])
    print(json.dumps(res, indent=2, ensure_ascii=False))
'''

'''
“Show the top 3 customers by total points_balance and include their lifetime spend.”	Loyalty ▲ Customer ▲ Orders	name · tier · points · total_amount
“Rank suppliers by average product rating.”	Supplier ▲ Product ▲ Review	supplier · avg_rating
Which couriers delivered the most shipments and what was their average delivery time?”	Shipment	courier · shipments · avg_days
“During the Holiday Sale promotion, how many units of each product were sold?”
'''




"""
GraphRAG Chain – Gemini Version (Updated for multi-table joins & robust querying)
"""

import os, sqlite3, json, sys, time
from typing import Dict, List
from dotenv import load_dotenv

# ---------------- Config -----------------------------------------------------
USE_FILTERED_SCHEMA = True   # ← flip to False for “full schema” baseline
FUZZY_THRESHOLD     = 60     # partial‑ratio % for table‑name match

# 0. Load env vars ------------------------------------------------------------
load_dotenv()

# 1. LangChain-Gemini ---------------------------------------------------------
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# 2. Neo4j --------------------------------------------------------------------
from py2neo import Graph as NeoGraph

# 3. Prompt utils -------------------------------------------------------------
from langchain.prompts import PromptTemplate
from fuzzywuzzy import fuzz
import tiktoken

# 4. ENV constants ------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or sys.exit("Missing GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PW   = os.getenv("NEO4J_PASSWORD", "Parthib@0103")
SQLITE_PATH= os.getenv("SQLITE_PATH", "db/retail.db")

# 5. Instantiate resources ----------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.0,
)
neo       = NeoGraph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PW))
sql_conn  = sqlite3.connect(SQLITE_PATH)
sql_conn.row_factory = sqlite3.Row

tok = tiktoken.encoding_for_model("gpt-4o-mini")   # token counter

# 6. Schema retrieval ---------------------------------------------------------
TABLES = ["Customer","OrderItem","Orders","Product","Store","Supplier","Review", "Payment", "Shipment", "Inventory", "Promotion", "ProductPromotion", "Loyalty"]

def _get_relevant_tables(question: str) -> List[str]:
    if not USE_FILTERED_SCHEMA:
        return TABLES
    hits = [tbl for tbl in TABLES if fuzz.partial_ratio(tbl.lower(), question.lower()) >= FUZZY_THRESHOLD]
    return hits if hits else TABLES

def _get_schema_context(question: str) -> str:
    relevant = _get_relevant_tables(question)
    question_lower = question.lower()

    
    if "promotion" in question_lower or "discount" in question_lower or "sale" in question_lower:
        for table in ["ProductPromotion", "OrderItem", "Orders"]:
            if table not in relevant:
                relevant.append(table)

    if "point" in question_lower or "loyalty" in question_lower:
        for table in ["Loyalty", "Orders"]:
            if table not in relevant:
                relevant.append(table)

    if "inventory" in question_lower or "stock" in question_lower:
        for table in ["Inventory", "Product", "Store"]:
            if table not in relevant:
                relevant.append(table)

    if "shipment" in question_lower or "delivery" in question_lower:
        for table in ["Shipment", "Orders", "Customer"]:
            if table not in relevant:
                relevant.append(table)

    if "payment" in question_lower or "transaction" in question_lower:
        for table in ["Payment", "Orders"]:
            if table not in relevant:
                relevant.append(table)

    if "review" in question_lower or "rating" in question_lower:
        for table in ["Review", "Product", "Customer"]:
            if table not in relevant:
                relevant.append(table)

    if "supplier" in question_lower or "vendor" in question_lower:
        for table in ["Supplier", "Product"]:
            if table not in relevant:
                relevant.append(table)

    if "order" in question_lower and "product" in question_lower:
        for table in ["OrderItem", "Orders", "Product"]:
            if table not in relevant:
                relevant.append(table)


    print(f"[DEBUG] Tables sent to Gemini: {relevant}")  # keep this log

    # Get table-column schema
    rows = neo.run("""
        MATCH (t:Table)-[:HAS_COLUMN]->(c:Column)
        WHERE t.name IN $tables
        RETURN t.name AS table, collect(c.name) AS cols
    """, parameters={"tables": relevant}).data()

    lines = [f"- {r['table']}({', '.join(sorted(r['cols']))})" for r in rows]

    # Get foreign keys
    fk_rows = neo.run("""
        MATCH (from:Column)-[:FOREIGN_KEY]->(to:Column)
        MATCH (ft:Table)-[:HAS_COLUMN]->(from)
        MATCH (tt:Table)-[:HAS_COLUMN]->(to)
        WHERE ft.name IN $tables AND tt.name IN $tables
        RETURN ft.name AS ft, from.name AS fc, tt.name AS tt, to.name AS tc
    """, parameters={"tables": relevant}).data()

    for r in fk_rows:
        lines.append(f"- FK: {r['ft']}.{r['fc']} ➜ {r['tt']}.{r['tc']}")

    return "\n".join(lines)

SCHEMA_PROMPT = """
You are an expert database assistant.
Generate ONLY a valid **SQLite** SQL query,
using exactly the tables & columns provided.
Ensure:
- Correct JOINs based on FK relationships.
- Proper GROUP BY when using aggregates.
- Avoid extra dialect (PostgreSQL/MySQL).
- Do not use markdown/code fences.

Schema:
{schema}

Question:
{question}

SQL:
"""

# 7. NLQ ➜ SQL ---------------------------------------------------------------
def nlq_to_sql(question: str, retry: bool = True) -> str:
    prompt = PromptTemplate(
        template=SCHEMA_PROMPT, input_variables=["schema", "question"]
    ).format(schema=_get_schema_context(question), question=question)
    print(prompt)
    token_count = len(tok.encode(prompt))
    t0 = time.time()

    response = llm.invoke(prompt)
    latency = time.time() - t0
    is_filtered = os.getenv("USE_FILTERED_SCHEMA", "true").lower() == "true"
    print(f"[Metrics] tokens={token_count} | LLM latency={latency:.2f}s | filtered={is_filtered}")

    sql = response.content.strip()
    sql = response.content.strip()

    # Optional fix for hallucinated table
    sql = sql.replace("FROM Sales", "FROM OrderItem")
    sql = sql.replace("JOIN Sales", "JOIN OrderItem")

    if sql.startswith("```"):
        sql = sql.split("```")[1].strip()

    if not sql.lower().startswith("select"):
        raise ValueError(f"❌ Invalid SQL generated:\n{sql}")

    return sql

# 8. Execute SQL with retry logic ---------------------------------------------
def run_sql(sql: str, question: str, _retry=False) -> Dict:
    try:
        cur = sql_conn.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        cols = [d[0] for d in cur.description]
        return {"sql": sql, "columns": cols, "rows": rows, "error": None}
    except sqlite3.OperationalError as e:
        if not _retry and "syntax" in str(e).lower():
            print("[RETRY] Fixing syntax error using LLM")
            fix_prompt = f"Original SQL:\n{sql}\n\nError:\n{str(e)}\n\nFix SQL only:"
            fixed = llm.invoke(fix_prompt).content.strip()
            if fixed.startswith("```"):
                fixed = fixed.split("```")[1].strip()
            return run_sql(fixed, question, _retry=True)
        return {"sql": sql, "columns": [], "rows": [], "error": str(e)}

# 9. Pipeline -----------------------------------------------------------------
def nlq_pipeline(q: str) -> Dict:
    sql = nlq_to_sql(q)
    print("\n🔍 SQL:\n", sql)
    return run_sql(sql, q)

# 10. CLI ---------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python graphrag_chain.py \"<question>\"")
    res = nlq_pipeline(sys.argv[1])
    print(json.dumps(res, indent=2, ensure_ascii=False))
