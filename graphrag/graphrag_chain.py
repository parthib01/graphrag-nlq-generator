"""
GraphRAG Chain – Gemini Version  (with token / latency metrics)
Author: M3
"""

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
sql_conn  = sqlite3.connect(SQLITE_PATH)
sql_conn.row_factory = sqlite3.Row

tok = tiktoken.encoding_for_model("gpt-4o-mini")   # any OpenAI‑compatible enc

# 6. Schema retrieval ---------------------------------------------------------
TABLES = ["Customer","OrderItem","Orders","Product","Store","Supplier","Review"]

def _get_relevant_tables(question: str) -> List[str]:
    if not USE_FILTERED_SCHEMA:           # full mode
        return TABLES
    hits = [tbl for tbl in TABLES
            if fuzz.partial_ratio(tbl.lower(), question.lower()) >= FUZZY_THRESHOLD]
    return hits if hits else TABLES       # fallback to full

def _get_schema_context(question: str) -> str:
    relevant = _get_relevant_tables(question)
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
