"""
test_optimizer.py
Simple tests for optimizer.py — no pytest needed, just run this file:
    python test_optimizer.py
"""

from optimizer import optimize_budget, calculate_risk_reduction


def test_never_exceeds_budget():
    controls = [
        {"id": "a", "name": "A", "cost": 600000, "risk_reduction": 0.5},
        {"id": "b", "name": "B", "cost": 600000, "risk_reduction": 0.5},
    ]
    result = optimize_budget(1000000, controls)
    assert result["total_cost"] <= 1000000, "Optimizer exceeded budget!"
    print("PASS: test_never_exceeds_budget")


def test_picks_best_combo_5_controls():
    controls = [
        {"id": "mfa", "name": "MFA", "cost": 200000, "risk_reduction": 0.15},
        {"id": "edr", "name": "EDR", "cost": 500000, "risk_reduction": 0.30},
        {"id": "patch", "name": "Patch Management", "cost": 100000, "risk_reduction": 0.10},
        {"id": "backup", "name": "Backup", "cost": 300000, "risk_reduction": 0.20},
        {"id": "training", "name": "Training", "cost": 50000, "risk_reduction": 0.08},
    ]

    result = optimize_budget(1000000, controls)

    expected_selected = {"edr", "patch", "backup", "training"}

    assert set(result["selected_controls"]) == expected_selected
    assert result["total_cost"] == 950000
    assert result["remaining_budget"] == 50000
    assert result["risk_reduction"] == 0.5363

    print("Selected:", result["selected_controls"])
    print("Total cost:", result["total_cost"])
    print("Risk reduction:", result["risk_reduction"])
    print("PASS: test_picks_best_combo_5_controls")


def test_risk_reduction_never_reaches_100_percent():
    controls = [
        {"id": "x", "name": "X", "cost": 1, "risk_reduction": 0.9},
        {"id": "y", "name": "Y", "cost": 1, "risk_reduction": 0.9},
        {"id": "z", "name": "Z", "cost": 1, "risk_reduction": 0.9},
    ]
    reduction = calculate_risk_reduction(controls)
    assert reduction < 1.0, "Combined risk reduction should never reach 100%"
    print("Combined reduction of three 90% controls:", round(reduction, 4))
    print("PASS: test_risk_reduction_never_reaches_100_percent")


def test_empty_controls_returns_zero():
    result = optimize_budget(1000000, [])
    assert result["selected_controls"] == []
    assert result["total_cost"] == 0
    assert result["risk_reduction"] == 0
    print("PASS: test_empty_controls_returns_zero")


def test_budget_too_small_for_anything():
    controls = [
        {"id": "expensive", "name": "Expensive Control", "cost": 999999999, "risk_reduction": 0.9},
    ]
    result = optimize_budget(1000, controls)
    assert result["selected_controls"] == []
    print("PASS: test_budget_too_small_for_anything")


if __name__ == "__main__":
    test_never_exceeds_budget()
    test_picks_best_combo_5_controls()
    test_risk_reduction_never_reaches_100_percent()
    test_empty_controls_returns_zero()
    test_budget_too_small_for_anything()
    print("\nAll tests passed!")
