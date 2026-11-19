import asyncio

from app.agents.framework_agents import create_agents
from app.business import get_order_context


async def run_agent(agent, message):
    result = await agent.run(message)

    return {
        "agent": agent.name,
        "response": str(result),
    }


async def investigate(order_id):
    order = get_order_context(order_id)
    agents = create_agents()

    context = (
        "QuickKart order data:\n"
        f"{order}\n\n"
        "Investigate this order. Use only the provided facts."
    )

    outputs = []

    # 1. Planner
    planner = await run_agent(agents["planner"], context)
    outputs.append(planner)

    # 2. Order specialist
    order_result = await run_agent(
        agents["order"],
        context + "\nPlanner findings:\n" + planner["response"],
    )
    outputs.append(order_result)

    # 3. Payment specialist
    payment_result = await run_agent(
        agents["payment"],
        context + "\nPlanner findings:\n" + planner["response"],
    )
    outputs.append(payment_result)

    # 4. Inventory specialist
    inventory_result = await run_agent(
        agents["inventory"],
        context + "\nPlanner findings:\n" + planner["response"],
    )
    outputs.append(inventory_result)

    # 5. Customer communication specialist
    specialist_findings = (
        f"Order: {order_result['response']}\n"
        f"Payment: {payment_result['response']}\n"
        f"Inventory: {inventory_result['response']}"
    )

    customer_result = await run_agent(
        agents["customer"],
        context + "\nSpecialist findings:\n" + specialist_findings,
    )
    outputs.append(customer_result)

    # 6. Supervisor
    supervisor_result = await run_agent(
        agents["supervisor"],
        context + "\nSpecialist findings:\n" + specialist_findings
        + "\nCustomer communication draft:\n"
        + customer_result["response"],
    )
    outputs.append(supervisor_result)

    return {
        "order_id": order_id,
        "agents": outputs,
        "final_report": supervisor_result["response"],
    }


def investigate_sync(order_id):
    return asyncio.run(investigate(order_id))