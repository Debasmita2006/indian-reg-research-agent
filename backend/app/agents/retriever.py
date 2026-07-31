import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Domains we trust more for Indian regulatory/policy content
PRIORITY_DOMAINS = [
    "rbi.org.in",
    "sebi.gov.in",
    "egazette.gov.in",
    "pib.gov.in",
    "meity.gov.in",
    "indiacode.nic.in"
]

def retrieve_for_subquestion(sub_question: str, max_results: int = 4) -> list[dict]:
    """
    Searches the web for a sub-question, prioritizing known Indian regulatory domains.
    Returns a list of {title, url, content, is_priority_source}.
    """
    response = tavily_client.search(
        query=sub_question,
        search_depth="advanced",
        max_results=max_results,
        include_raw_content=False,
    )

    results = []
    for item in response.get("results", []):
        url = item.get("url", "")
        is_priority = any(domain in url for domain in PRIORITY_DOMAINS)
        results.append({
            "title": item.get("title", ""),
            "url": url,
            "content": item.get("content", ""),
            "is_priority_source": is_priority,
        })

    # Sort so priority (official regulatory) sources appear first
    results.sort(key=lambda x: not x["is_priority_source"])
    return results


def retrieve_all(sub_questions: list[str]) -> dict[str, list[dict]]:
    """
    Runs retrieval for every sub-question, returns a dict mapping
    sub-question -> list of sources.
    """
    all_results = {}
    for sq in sub_questions:
        all_results[sq] = retrieve_for_subquestion(sq)
    return all_results