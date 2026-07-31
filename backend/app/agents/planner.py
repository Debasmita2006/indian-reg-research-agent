import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PLANNER_SYSTEM_PROMPT = """You are a research planning agent specialized in Indian regulatory and policy topics
(RBI/SEBI circulars, government notifications, gazette publications, court judgments, state policies).

Given a user's research question, break it down into 3-5 focused sub-questions that, when answered,
would together provide a complete picture. Sub-questions should be specific and searchable.

Respond ONLY with a JSON object in this exact format, no other text:
{"sub_questions": ["question 1", "question 2", "question 3"]}
"""

def plan_query(user_query: str) -> list[str]:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        temperature=0.3,
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw_output)
        return parsed["sub_questions"]
    except (json.JSONDecodeError, KeyError):
        # Fallback: if the model didn't return clean JSON, treat the whole query as one sub-question
        return [user_query]