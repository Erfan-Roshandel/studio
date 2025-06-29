# agent.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Dict, Any

class AgentState(TypedDict):
    data: dict
    metrics: Optional[dict]
    report: Optional[dict]

def input_node(state: AgentState) -> dict:
    return {"data": state["data"]}

def processing_node(state: AgentState) -> dict:
    data = state["data"]
    rev = data.get("revenue", 0)
    cost = data.get("cost", 0)
    prev_rev = data.get("prev_revenue")
    prev_cost = data.get("prev_cost")
    cust = data.get("customers", 1)
    prev_cust = data.get("prev_customers", 1)
    
    # Calculate metrics
    profit = rev - cost
    profit_status = "profit" if profit >= 0 else "loss"
    
    rev_chg = ((rev - prev_rev) / prev_rev * 100) if prev_rev and prev_rev != 0 else None
    cost_chg = ((cost - prev_cost) / prev_cost * 100) if prev_cost and prev_cost != 0 else None
    
    cac = cost / cust
    prev_cac = prev_cost / prev_cust if prev_cost and prev_cust and prev_cust != 0 else None
    cac_chg = ((cac - prev_cac) / prev_cac * 100) if prev_cac and prev_cac != 0 else None

    return {
        "metrics": {
            "profit": profit,
            "profit_status": profit_status,
            "revenue_change": rev_chg,
            "cost_change": cost_chg,
            "cac": cac,
            "cac_change": cac_chg
        }
    }

def recommendation_node(state: AgentState) -> dict:
    metrics = state["metrics"]
    alerts = []
    recommendations = []
    
    # Profit check
    if metrics["profit"] < 0:
        alerts.append(f"Loss detected: ${abs(metrics['profit'])}")
        recommendations.append("Reduce operational costs immediately")
    
    # CAC change check
    if metrics["cac_change"] is not None and metrics["cac_change"] > 20:
        alerts.append(f"CAC increased by {metrics['cac_change']:.1f}%")
        recommendations.append("Review marketing campaigns and channels")
    
    # Revenue growth opportunity
    if metrics["revenue_change"] is not None and metrics["revenue_change"] > 0:
        recommendations.append(
            f"Increase advertising budget (sales up {metrics['revenue_change']:.1f}%)"
        )
    
    return {
        "report": {
            "profit_status": metrics["profit_status"],
            "alerts": alerts,
            "recommendations": recommendations
        }
    }

def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("input", input_node)
    graph.add_node("processing", processing_node)
    graph.add_node("recommendations", recommendation_node)
    
    graph.set_entry_point("input")
    graph.add_edge("input", "processing")
    graph.add_edge("processing", "recommendations")
    graph.add_edge("recommendations", END)
    
    return graph.compile()

def run_agent(data: dict) -> dict:
    app = build_graph()
    result = app.invoke({"data": data})
    return result["report"]

if __name__ == "__main__":
    # Test sample
    test_data = {
        "revenue": 1200,
        "cost": 900,
        "prev_revenue": 1000,
        "prev_cost": 700,
        "customers": 50,
        "prev_customers": 40
    }
    
    result = run_agent(test_data)
    import json
    print("Test Result:\n", json.dumps(result, indent=2))
    with open("output.json", "w") as g:
        json.dump(result, g, indent=2)
    
    # Save graph configuration
    graph = build_graph()
    with open("business_analyst_agent.json", "w") as f:
        json.dump({
            "nodes": ["input", "processing", "recommendations"],
            "edges": [
                ("input", "processing"),
                ("processing", "recommendations")
            ],
            "entry_point": "input",
            "end_points": ["recommendations"]
        }, f, indent=2)