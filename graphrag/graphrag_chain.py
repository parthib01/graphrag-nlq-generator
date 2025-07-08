"""
GraphRAG Chain – Gemini Version
Author: M3
Description:
    Natural‑language query  ➜  Gemini (with Neo4j schema context)  ➜  SQL
    Executes on SQLite (retail.db) and returns rows in JSON‑friendly format.
"""

import os, sqlite3, json, sys, time
from typing import Dict, List

# ── 0. Load .env ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()                          # ensures GEMINI_API_KEY & SQLITE_PATH set

# ── 1.  Gemini LLM via LangChain wrapper ──────────────────────────────────────
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# ── 2.  Neo4j connection (schema graph) ───────────────────────────────────────
from py2neo import Graph as NeoGraph

# ── 3.  Prompt utils ──────────────────────────────────────────────────────────
from langchain.prompts import PromptTemplate

# ── 4.  ENV & constants ───────────────────────────────────────────────────────
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌  GEMINI_API_KEY is missing.  Add it to .env or shell.")
genai.configure(api_key=GEMINI_API_KEY)

NEO4J_URI       = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER      = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD  = os.getenv("NEO4J_PASSWORD", "Parthib@0103")
SQLITE_PATH     = os.getenv("SQLITE_PATH", "db/retail.db")   # relative path ok

# ── 5.  Instantiate resources ────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",      # use gemini‑pro if flash isn’t enabled
    google_api_key=GEMINI_API_KEY,
    temperature=0.0,
)
neo = NeoGraph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
sql_conn = sqlite3.connect(SQLITE_PATH)
sql_conn.row_factory = sqlite3.Row

# ── 6.  Build schema context from Neo4j ───────────────────────────────────────
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

def _get_schema_context() -> str:
    """Return tables, columns and foreign keys in bullet form."""
    # Tables + columns
    rows = neo.run("""
        MATCH (t:Table)-[:HAS_COLUMN]->(c:Column)
        RETURN t.name AS table, collect(c.name) AS cols
    """).data()
    lines = [f"- {r['table']}({', '.join(sorted(r['cols']))})" for r in rows]

    # Foreign keys
    fk_rows = neo.run("""
        MATCH (from:Column)-[:FOREIGN_KEY]->(to:Column)
        MATCH (ft:Table)-[:HAS_COLUMN]->(from)
        MATCH (tt:Table)-[:HAS_COLUMN]->(to)
        RETURN ft.name AS ft, from.name AS fc, tt.name AS tt, to.name AS tc
    """).data()
    for r in fk_rows:
        lines.append(f"- FK: {r['ft']}.{r['fc']} ➜ {r['tt']}.{r['tc']}")

    return "\n".join(lines)

# ── 7.  NLQ ➜ SQL with optional retry ────────────────────────────────────────
def nlq_to_sql(question: str, retry: bool = True) -> str:
    prompt = PromptTemplate(
        template=SCHEMA_PROMPT, input_variables=["schema", "question"]
    ).format(schema=_get_schema_context(), question=question)

    response = llm.invoke(prompt)
    sql = response.content.strip()

    # Remove accidental markdown fences if any
    if sql.startswith("```"):
        sql = sql.split("```")[1].strip()
    return sql

# ── 8.  Run SQL safely & retry once on error ─────────────────────────────────
def run_sql(sql: str, question: str, *, _has_retried: bool = False) -> Dict:
    """
    Execute SQL safely.
    • If a syntax error occurs, ask Gemini to fix it **once**.
    • If the second attempt still fails, return the error.
    """
    try:
        cur = sql_conn.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        cols = [d[0] for d in cur.description]
        return {"sql": sql, "columns": cols, "rows": rows, "error": None}

    except sqlite3.OperationalError as e:
        # Only retry once and only for syntax‑type errors
        if (not _has_retried) and "syntax" in str(e).lower() and question:
            fix_prompt = (
                f"The previous SQL caused this SQLite error:\n{e}\n"
                f"Please correct the query. Respond with SQL only."
            )
            fixed_sql = llm.invoke(fix_prompt).content.strip()
            if fixed_sql.startswith("```"):
                fixed_sql = fixed_sql.split("```")[1].strip()
            # Retry exactly once
            return run_sql(fixed_sql, question, _has_retried=True)

        # Either we already retried or it's not a syntax error → return failure
        return {
            "sql": sql,
            "columns": [],
            "rows": [],
            "error": str(e)
        }


# ── 9.  Full pipeline wrapper ────────────────────────────────────────────────
def nlq_pipeline(question: str) -> Dict:
    sql = nlq_to_sql(question)
    print("\n🔍  Generated SQL:\n", sql)          # helpful debug print
    result = run_sql(sql, question)
    return result

# ── 10.  CLI Test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python graphrag_chain.py \"<your NL question>\"")
        sys.exit(1)

    t0 = time.time()
    out = nlq_pipeline(sys.argv[1])
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n✅  Done in {time.time()-t0:.2f}s")
