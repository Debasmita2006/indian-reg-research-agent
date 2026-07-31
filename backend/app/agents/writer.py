import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

WRITER_SYSTEM_PROMPT = """You are a research report writer specialized in Indian regulatory and policy topics.

You will be given the original user query, and for each sub-question: a list of verified facts (with supporting URLs)
and any contradictions found between sources.

Write a clear, well-structured report that:
1. Directly answers the original query
2. Is organized into logical sections (not necessarily one section per sub-question verbatim)
3. Cites sources inline using [Source: URL] after each factual claim
4. Explicitly mentions any unresolved contradictions or uncertainty, rather than hiding them
5. Uses plain, professional language — no fluff, no unsupported claims

Do not invent any facts not present in the verified facts provided."""

def write_report(original_query: str, verified_data: dict[str, dict]) -> str:
    context_blocks = []
    for sub_q, data in verified_data.items():
        facts = data.get("verified_facts", [])
        contradictions = data.get("contradictions", [])

        facts_text = "\n".join([
            f"- {f['fact']} [Source: {', '.join(f['supporting_urls'])}]"
            for f in facts
        ])
        contradictions_text = "\n".join([
            f"- ISSUE: {c['issue']} | RESOLUTION: {c['resolution']}"
            for c in contradictions
        ])

        block = f"Sub-question: {sub_q}\nVerified facts:\n{facts_text}\n"
        if contradictions_text:
            block += f"Contradictions found:\n{contradictions_text}\n"
        context_blocks.append(block)

    full_context = "\n\n".join(context_blocks)
    user_content = f"Original query: {original_query}\n\n{full_context}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": WRITER_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()