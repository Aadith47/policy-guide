import json
import os

from google import genai

from search import search

# Flash is fast and cheap, good enough for this task
MODEL_NAME = "gemini-3.5-flash-lite"
VALID_VERDICTS = {"Allowed", "Violation", "Unclear"}

# Strict prompt: only the excerpts, a fixed JSON shape, and "Unclear" as the safe default
PROMPT_TEMPLATE = """You are a policy assistant for new employees.
Answer ONLY from the excerpts below. Do not use outside knowledge.

Rules:
- If the excerpts clearly answer the question, use "Allowed" or "Violation".
- If they do not clearly cover it, use "Unclear" and tell the person to ask HR.
- Name the page of the excerpt you relied on.
- Reply with JSON only, with these keys: verdict, reason, page, next_step.

Excerpts:
{excerpts}

Question: {question}
"""


def format_excerpts(hits):
    # Label each excerpt with its page so the model can cite it
    parts = [f"[page {hit['page']}]\n{hit['text']}" for hit in hits]
    return "\n\n".join(parts)


def parse_answer(raw_text):
    # Models sometimes wrap JSON in code fences, so strip them before parsing
    cleaned = raw_text.strip().strip("`")
    if cleaned.startswith("json"):
        cleaned = cleaned[4:]

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:

            # Fill gaps so the app never shows None
        data["reason"] = data.get("reason") or "No reason was given."
        data["next_step"] = data.get("next_step") or "If you are unsure, ask HR."
        
        # If the reply is not valid JSON, fail safe instead of guessing
        return {
            "verdict": "Unclear",
            "reason": "The answer could not be read. Please ask HR.",
            "page": None,
            "next_step": "Contact HR.",
        }

    # Never trust a verdict we did not ask for
    if data.get("verdict") not in VALID_VERDICTS:
        data["verdict"] = "Unclear"
    return data


def answer_question(question):
    # Read the key from the environment, never from the code
    api_key = os.environ["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

    hits = search(question)
    prompt = PROMPT_TEMPLATE.format(
        excerpts=format_excerpts(hits),
        question=question,
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    return parse_answer(response.text)


if __name__ == "__main__":
    # Simple loop so you can ask many questions without restarting
    while True:
        question = input("\nAsk a policy question (or press Enter to quit): ").strip()
        if not question:
            break

        answer = answer_question(question)
        print(f"\nVerdict: {answer['verdict']}")
        print(f"Reason:  {answer['reason']}")
        print(f"Page:    {answer['page']}")
        print(f"Next:    {answer['next_step']}")