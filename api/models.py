from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# ---------- Request ----------
class NLQRequest(BaseModel):
    question: str

# ---------- Response ----------
class NLQResponse(BaseModel):
    query: str                      # original NLQ
    sql_query: str                  # generated SQL
    output: List[Dict[str, Any]]    # rows from SQLite
    insight: str                    # Gemini summary
    error: Optional[str] = None     # populated only on failure


#uvicorn api.main:app --reload --log-level debug
