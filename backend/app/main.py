from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.graph import run_agent
from app.db.session import init_db, SessionLocal
from app.db.models import QueryLog

app = FastAPI(title="Indian Regulatory Research Agent")

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later for production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


class QueryRequest(BaseModel):
    query: str


@app.post("/api/research")
def research(request: QueryRequest):
    result = run_agent(request.query)
    return {
        "original_query": result["original_query"],
        "sub_questions": result["sub_questions"],
        "final_report": result["final_report"],
        "eval_result": result["eval_result"],
        "latency_seconds": result["latency_seconds"],
        "contradictions_by_subquestion": {
            sq: v.get("contradictions", []) for sq, v in result["verified_data"].items()
        },
    }


@app.get("/api/dashboard")
def dashboard():
    db = SessionLocal()
    try:
        logs = db.query(QueryLog).order_by(QueryLog.created_at.asc()).all()
        return [
            {
                "id": log.id,
                "query": log.user_query,
                "faithfulness_score": log.faithfulness_score,
                "relevance_score": log.relevance_score,
                "completeness_score": log.completeness_score,
                "latency_seconds": log.latency_seconds,
                "contradictions_found": log.contradictions_found,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}