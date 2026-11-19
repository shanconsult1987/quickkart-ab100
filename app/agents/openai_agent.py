from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL, validate_configuration


SYSTEM_PROMPT = """
You are the QuickKart Operations Investigation Assistant.

Your job is to investigate an order using only the supplied business data.

Rules:
1. Do not invent payment, inventory or delivery information.
2. Clearly distinguish known facts from assumptions.
3. Identify the issue affecting the order.
4. Explain the operational impact.
5. Recommend the next safe action.
6. Never claim that a refund, cancellation or payment action has occurred.
7. Escalate uncertain or financially sensitive decisions to a human.

Return a concise operational report with:
- Order summary
- Findings
- Root cause or likely cause
- Recommended next step
- Human approval required: Yes or No
"""


def investigate_order(order):
    validate_configuration()

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=f"Investigate this QuickKart order:\n{order}",
    )

    usage = getattr(response, "usage", None)

    return {
        "agent": "OpenAIInvestigationAgent",
        "model": OPENAI_MODEL,
        "response": response.output_text,
        "usage": {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
            "total_tokens": getattr(usage, "total_tokens", 0),
        },
        "response_id": getattr(response, "id", None),
    }