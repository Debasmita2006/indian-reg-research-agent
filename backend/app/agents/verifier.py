import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

VERIFIER_SYSTEM_PROMPT = """You are a fact-verification agent. You will be given a sub-question and a list of
sources (each with a URL, content snippet, and whether it's an official priority source like RBI/SEBI/PIB/gazette).

Your job:
1. Identify the key factual claims relevant to the sub-question across all sources.
2. Detect any CONTRADICTIONS between sources (e.g. different numbers, dates, or statuses for the same fact).
3. When a contradiction exists, prefer the priority source's claim, and note the discrepancy.
4. Produce a short list of VERIFIED facts (with which source(s) support each), plus a list of CONTRADICTIONS found.

Respond ONLY with JSON in this exact format:
{
  "verified_facts": [
    {"fact": "...", "supporting_urls": ["..."]}
  ],
  "contradictions": [
    {"issue": "...", "sources_involved": ["..."], "resolution": "..."}
  ]
}
"""

def verify_sources(sub_question: str, sources: list[dict]) -> dict:
    sources_text = "\n\n".join([
        f"Source {i+1} (priority={s['is_priority_source']}): {s['url']}\n{s['content'][:800]}"
        for i, s in enumerate(sources)
    ])

    user_content = f"Sub-question: {sub_question}\n\nSources:\n{sources_text}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": VERIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2,
    )

    raw_output = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model wrapped the JSON in them
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.startswith("json"):
            raw_output = raw_output[4:].strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {"verified_facts": [], "contradictions": [], "raw_error_output": raw_output}


def verify_all(retrieval_results: dict[str, list[dict]]) -> dict[str, dict]:
    """
    Runs verification for every sub-question's retrieved sources.
    Returns dict mapping sub-question -> {verified_facts, contradictions}
    """
    verified = {}
    for sq, sources in retrieval_results.items():
        verified[sq] = verify_sources(sq, sources)
    return verified