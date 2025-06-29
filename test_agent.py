import pytest
from agent import run_agent

def test_positive_growth():
    data = {
        "revenue": 2000,
        "cost": 1000,
        "prev_revenue": 1500,
        "prev_cost": 900,
        "customers": 100,
        "prev_customers": 80
    }
    result = run_agent(data)
    assert result["profit_status"] == "profit"
    assert any("Increase advertising budget" in r for r in result["recommendations"])
    assert len(result["alerts"]) == 0

def test_loss_high_cac():
    data = {
        "revenue": 500,
        "cost": 800,
        "prev_revenue": 600,
        "prev_cost": 500,
        "customers": 20,
        "prev_customers": 50
    }
    result = run_agent(data)
    assert result["profit_status"] == "loss"
    assert any("Reduce operational costs" in r for r in result["recommendations"])
    assert any("CAC increased" in a for a in result["alerts"])

def test_no_previous_data():
    data = {
        "revenue": 1000,
        "cost": 700,
        "customers": 30
    }
    result = run_agent(data)
    assert result["profit_status"] == "profit"
    assert len(result["alerts"]) == 0
    assert len(result["recommendations"]) == 0