from smolagents.models import LiteLLMModel

model = LiteLLMModel(model_id="ollama/phi3")

def summarize(text: str, style: str = "short") -> str:
    if style == "short":
        instruction = "Summarize the text in 5 bullet points. Then add 1-line TL;DR."
    elif style == "detailed":
        instruction = (
            "Write a structured summary with headings: Overview, Key Points, "
            "Decisions (if any), Action Items (if any)."
        )
    else:
        instruction = "Summarize clearly."

    prompt = f"""
    You are a strict text summarizer.

    STRICT RULES (must follow):
    1) Do NOT add new dates, day names, or numbers.
    2) If a date/number appears in the text, copy it EXACTLY (same digits).
    3) If a date/number is NOT in the text, write: "Not mentioned".
    4) Do NOT guess or infer.
    5) Output format must be exactly:
    - Bullet 1
    - Bullet 2
    - Bullet 3
    - Bullet 4
    - Bullet 5
    TL;DR: one line

    TEXT:
    {text}

    TASK:
    Summarize in 5 bullets + TL;DR.
    """.strip()



    # ✅ smolagents LiteLLMModel expects chat messages
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    resp = model(messages)
    return resp.content



if __name__ == "__main__":
    sample = """
    Today we discussed the launch plan. The team will finalize the UI by Friday.
    Marketing will prepare creatives by next Wednesday. The release date is March 10.
    Risks: payment gateway reliability and last-minute scope changes.
    """
    print(summarize(sample, style="short"))