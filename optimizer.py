"""
optimizer.py
Security Investment Optimizer — Team HexCell, SIH26105

WHAT THIS DOES
--------------
Given a fixed cybersecurity budget and a list of candidate security
controls (each with a cost and an estimated risk reduction), this
module finds the combination of controls that:

    1. Never exceeds the budget
    2. Produces the greatest overall reduction in cyber risk

METHOD (MVP)
------------
Brute force. For a small number of controls (roughly <= 20), you can
safely check every possible subset (2^n combinations) and pick the
best valid one. No fancier algorithm is needed yet — this is
intentional, per the MVP rule: don't sacrifice a working version for
algorithmic sophistication.

RISK REDUCTION MODEL — READ THIS BEFORE CHANGING ANYTHING
-----------------------------------------------------------
You CANNOT just add risk reductions together:

    MFA (15%) + EDR (30%)  !=  45%

Controls often overlap in what they protect (e.g. two controls might
both reduce the risk of the same phishing-based breach). Naive
addition double-counts that overlap and can even push "total risk
reduction" above 100%, which is meaningless.

Instead, this MVP uses the standard way of combining independent
probability-like reductions — a MULTIPLICATIVE / diminishing-returns
model:

    combined_reduction = 1 - (1 - r1) * (1 - r2) * ... * (1 - rn)

Intuition: each control only gets to reduce whatever risk is LEFT
after the previous controls, not the original 100%. This:
    - never exceeds 100%
    - naturally shows diminishing returns as you stack controls
    - is easy to explain to judges: "each control chips away at
      whatever risk remains"

ASSUMPTION THAT MUST BE STATED OUT LOUD:
    Each control's risk_reduction value is treated as INDEPENDENT of
    the others. In reality, some controls overlap heavily (e.g. two
    controls that both mitigate phishing), and this model will
    slightly OVER-estimate the combined benefit in those cases. This
    is a deliberate MVP simplification. It should eventually be
    replaced/validated using Vanshika's Monte Carlo model, which can
    directly compare simulated risk BEFORE vs AFTER a chosen set of
    controls instead of relying on this formula.

Everything below is example/synthetic data used only to demonstrate
the module. It is NOT a real-world statistic.
"""

import itertools
import json


def calculate_total_cost(controls):
    """Total cost of a list/tuple of control dicts."""
    return sum(c["cost"] for c in controls)


def calculate_risk_reduction(controls):
    """
    Combine each control's risk_reduction using the multiplicative
    (diminishing-returns) model described above.

    Returns a float between 0 and 1 (e.g. 0.55 = 55% combined
    reduction).
    """
    remaining_risk = 1.0
    for c in controls:
        remaining_risk *= (1 - c["risk_reduction"])
    return 1 - remaining_risk


def optimize_budget(budget, controls, annual_risk=None):
    """
    Brute-force optimizer.

    Parameters
    ----------
    budget : float
        Total available cybersecurity budget (e.g. in rupees).
    controls : list of dict
        Each dict must have at least: id, name, cost, risk_reduction
        (risk_reduction is a fraction between 0 and 1, e.g. 0.15 for 15%).
    annual_risk : float, optional
        Current annualized financial risk (in rupees) BEFORE applying
        any controls. If given, the output also reports estimated
        financial loss before/after in rupees.

    Returns
    -------
    dict (JSON-serializable):
        {
          "budget": ...,
          "selected_controls": [ids...],
          "total_cost": ...,
          "remaining_budget": ...,
          "risk_reduction": ...,             # 0-1
          "controls_considered_not_selected": [ids...],
          # only present if annual_risk was given:
          "expected_loss_before": ...,
          "expected_loss_after": ...
        }
    """
    best_combo = ()
    best_reduction = 0.0
    best_cost = 0

    n = len(controls)
    # Check every possible subset (2^n). Fine for small n (<= ~20).
    for r in range(0, n + 1):
        for combo in itertools.combinations(controls, r):
            cost = calculate_total_cost(combo)
            if cost > budget:
                continue
            reduction = calculate_risk_reduction(combo)
            # Prefer higher risk reduction; if tied, prefer lower cost.
            if (reduction > best_reduction) or (
                reduction == best_reduction and cost < best_cost
            ):
                best_combo = combo
                best_reduction = reduction
                best_cost = cost

    selected_ids = [c["id"] for c in best_combo]
    not_selected = [c["id"] for c in controls if c["id"] not in selected_ids]

    result = {
        "budget": budget,
        "selected_controls": selected_ids,
        "total_cost": best_cost,
        "remaining_budget": budget - best_cost,
        "risk_reduction": round(best_reduction, 4),
        "controls_considered_not_selected": not_selected,
    }

    if annual_risk is not None:
        expected_loss_before = annual_risk
        expected_loss_after = annual_risk * (1 - best_reduction)
        result["expected_loss_before"] = round(expected_loss_before, 2)
        result["expected_loss_after"] = round(expected_loss_after, 2)

    return result


if __name__ == "__main__":
    # ---- EXAMPLE / SYNTHETIC DATA — for demo only, not real stats ----
    example_controls = [
        {"id": "mfa", "name": "Multi-Factor Authentication", "cost": 200000, "risk_reduction": 0.15},
        {"id": "edr", "name": "Endpoint Detection and Response", "cost": 500000, "risk_reduction": 0.30},
        {"id": "patch", "name": "Patch Management", "cost": 100000, "risk_reduction": 0.10},
        {"id": "backup", "name": "Backup & Recovery", "cost": 300000, "risk_reduction": 0.20},
        {"id": "training", "name": "Security Awareness Training", "cost": 50000, "risk_reduction": 0.08},
    ]

    example_budget = 1000000       # ₹10,00,000 (synthetic)
    example_annual_risk = 42000000  # ₹4.2 Cr (synthetic)

    output = optimize_budget(example_budget, example_controls, example_annual_risk)
    print(json.dumps(output, indent=2))
