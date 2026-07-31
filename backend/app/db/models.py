from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False)
    sub_questions = Column(JSON)          # list of sub-questions generated
    sources_used = Column(JSON)           # list of {url, type, content_snippet}
    contradictions_found = Column(Integer, default=0)
    final_report = Column(Text)

    faithfulness_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)

    total_tokens = Column(Integer, nullable=True)
    latency_seconds = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)