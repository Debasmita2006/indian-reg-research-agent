import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

JUDGE_SYSTEM_PROMPT = """You are a strict evaluation judge for research reports. You will be given:
1. The original user query
2. The final report generated
3. The verified facts and contradictions that were supposed to ground the report

Score the report on three dimensions, each from 0.0 to 1.0:

- faithfulness: Does every factual claim in the report trace back to the verified facts provided?
  Penalize heavily if the report cites sources not relevant to the claim, or includes information
  that contradicts or isn't supported by the verified facts.
- relevance: Does the report actually answer the original query, without irrelevant tangents?
- completeness: Does the report address all the sub-questions' worth of ground, or leave gaps?

Also list specific issues found (e.g. "cited an irrelevant source for claim X", "included outdated
information without flagging it as such", "ignored a contradiction").

Respond ONLY with JSON in this exact format:
{
  "faithfulness_score": 0.0,
  "relevance_score": 0.0,
  "completeness_score": 0.0,
  "issues_found": ["..."]
}
"""

def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return text

def evaluate_report(original_query: str, report: str, verified_data: dict) -> dict:
    verified_summary = json.dumps(verified_data, indent=2)[:4000]  # cap size

    user_content = f"""Original query: {original_query}

Final report:
{report}

Verified facts and contradictions that were available:
{verified_summary}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.1,
    )

    raw_output = _strip_fences(response.choices[0].message.content.strip())

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "faithfulness_score": None,
            "relevance_score": None,
            "completeness_score": None,
            "issues_found": [],
            "raw_error_output": raw_output
        }