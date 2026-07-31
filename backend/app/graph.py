import time
from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.agents.planner import plan_query
from app.agents.retriever import retrieve_for_subquestion
from app.agents.verifier import verify_sources
from app.agents.writer import write_report
from app.eval.judge import evaluate_report
from app.db.session import SessionLocal
from app.db.models import QueryLog


class AgentState(TypedDict):
    original_query: str
    sub_questions: list
    retrieval_results: dict
    verified_data: dict
    final_report: str
    eval_result: dict
    start_time: float


def planner_node(state: AgentState) -> AgentState:
    state["sub_questions"] = plan_query(state["original_query"])
    return state


def retriever_node(state: AgentState) -> AgentState:
    results = {}
    for sq in state["sub_questions"]:
        results[sq] = retrieve_for_subquestion(sq)
    state["retrieval_results"] = results
    return state


def verifier_node(state: AgentState) -> AgentState:
    verified = {}
    for sq, sources in state["retrieval_results"].items():
        verified[sq] = verify_sources(sq, sources)
    state["verified_data"] = verified
    return state


def writer_node(state: AgentState) -> AgentState:
    state["final_report"] = write_report(state["original_query"], state["verified_data"])
    return state


def evaluator_node(state: AgentState) -> AgentState:
    state["eval_result"] = evaluate_report(
        state["original_query"], state["final_report"], state["verified_data"]
    )
    return state


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("writer", writer_node)
    graph.add_node("evaluator", evaluator_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "verifier")
    graph.add_edge("verifier", "writer")
    graph.add_edge("writer", "evaluator")
    graph.add_edge("evaluator", END)

    return graph.compile()


def run_agent(user_query: str, log_to_db: bool = True) -> dict:
    """
    Runs the full agent pipeline and logs the result to Postgres.
    Returns the final state dict.
    """
    app = build_graph()
    start_time = time.time()

    initial_state: AgentState = {
        "original_query": user_query,
        "sub_questions": [],
        "retrieval_results": {},
        "verified_data": {},
        "final_report": "",
        "eval_result": {},
        "start_time": start_time,
    }

    final_state = app.invoke(initial_state)
    latency = time.time() - start_time

    if log_to_db:
        total_contradictions = sum(
            len(v.get("contradictions", [])) for v in final_state["verified_data"].values()
        )
        sources_used = []
        for sq, sources in final_state["retrieval_results"].items():
            for s in sources:
                sources_used.append({"sub_question": sq, "url": s["url"], "is_priority": s["is_priority_source"]})

        eval_result = final_state.get("eval_result", {})

        log_entry = QueryLog(
            user_query=user_query,
            sub_questions=final_state["sub_questions"],
            sources_used=sources_used,
            contradictions_found=total_contradictions,
            final_report=final_state["final_report"],
            faithfulness_score=eval_result.get("faithfulness_score"),
            relevance_score=eval_result.get("relevance_score"),
            completeness_score=eval_result.get("completeness_score"),
            latency_seconds=latency,
        )

        db = SessionLocal()
        try:
            db.add(log_entry)
            db.commit()
        finally:
            db.close()

    final_state["latency_seconds"] = latency
    return final_state