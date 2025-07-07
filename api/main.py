from fastapi import FastAPI
from typing import List, Dict, Any

from graphrag.graphrag_chain import nlq_pipeline
from insight_generator.generator import generate_insight   # adjust path if needed
from .models import NLQRequest, NLQResponse

app = FastAPI(title="GraphRAG NLQ Insight API")

@app.post("/ask", response_model=NLQResponse)
async def ask_nlq(req: NLQRequest) -> NLQResponse:
    """
    End‑to‑end:
      NLQ → (M3) SQL + rows → (M4) insight → JSON
    """
    try:
        # ---- M3 step --------------------------------------------------------
        result = nlq_pipeline(req.question)
        sql_query: str = result["sql"]
        rows: List[Dict[str, Any]] = result["rows"]

        # ---- M4 step --------------------------------------------------------
        insight: str = generate_insight(req.question, rows)

        return NLQResponse(
            query=req.question,
            sql_query=sql_query,
            output=rows,
            insight=insight,
            error=None,
        )

    except Exception as exc:
        # Capture reason and send back to caller
        return NLQResponse(
            query=req.question,
            sql_query="",
            output=[],
            insight="",
            error=str(exc),
        )
