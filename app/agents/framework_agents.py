from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from app.config import OPENAI_API_KEY, OPENAI_MODEL, validate_configuration


def create_agents():
    validate_configuration()

    client = OpenAIChatClient(
        api_key=OPENAI_API_KEY,
        model=OPENAI_MODEL,
    )

    agents = {
        "planner": Agent(
            client=client,
            name="PlannerAgent",
            instructions="""
You are the QuickKart Planner Agent.

Read the supplied order data.
Create a short investigation plan.
Identify which specialist agents should investigate the case.
Do not invent data or execute transactions.
""",
        ),

        "order": Agent(
            client=client,
            name="OrderAgent",
            instructions="""
You are the QuickKart Order Agent.

Investigate order status and delivery information.
Identify delays and order risks.
Use only supplied data.
Never claim to update an order.
""",
        ),

        "payment": Agent(
            client=client,
            name="PaymentAgent",
            instructions="""
You are the QuickKart Payment Agent.

Investigate payment status.
Identify pending or failed payments.
Never initiate a payment or refund.
Escalate financially sensitive decisions.
""",
        ),

        "inventory": Agent(
            client=client,
            name="InventoryAgent",
            instructions="""
You are the QuickKart Inventory Agent.

Investigate inventory availability.
Identify shortages and stock-related risks.
Never change inventory.
Use only supplied data.
""",
        ),

        "customer": Agent(
            client=client,
            name="CustomerAgent",
            instructions="""
You are the QuickKart Customer Communication Agent.

Prepare a customer-friendly message based on supplied findings.
Do not claim that an action has been completed if it has not.
Do not disclose internal operational information.
""",
        ),

        "supervisor": Agent(
            client=client,
            name="SupervisorAgent",
            instructions="""
You are the QuickKart Supervisor Agent.

Consolidate the investigation findings.
Identify the most likely root cause.
List the evidence supporting the conclusion.
Recommend the next safe operational action.
Clearly identify whether human approval is required.
Do not invent facts or claim that a transaction occurred.
""",
        ),
    }

    return agents