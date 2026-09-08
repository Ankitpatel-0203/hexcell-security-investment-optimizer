import random
import itertools

# ---------- Risk Simulation ----------
def simulate_risk(events, simulations=10000, seed=42):
    random.seed(seed)
    losses = []
    for _ in range(simulations):
        total_loss = 0
        for e in events:
            if random.random() < e["likelihood"]:
                total_loss += random.randint(e["impact_min"], e["impact_max"])
        losses.append(total_loss)
    losses.sort()
    n = len(losses)
    return {"expected_loss": sum(losses) / n, "p50_loss": losses[int(0.50 * n)],"p95_loss": losses[int(0.95 * n)],}

# ---------- Optimizer ----------
def combined_reduction(combo):
    remaining = 1
    for c in combo:
        remaining *= (1 - c["risk_reduction"])
    return 1 - remaining
def optimize_budget(budget, controls):
    best = ()
    best_reduction = 0
    for r in range(len(controls) + 1):
        for combo in itertools.combinations(controls, r):
            cost = sum(c["cost"] for c in combo)
            if cost <= budget:
                reduction = combined_reduction(combo)
                if reduction > best_reduction:
                    best = combo
                    best_reduction = reduction

    return best_reduction, [c["id"] for c in best]

# ---------- Synthetic Data ----------
events = [{"name":"Phishing","likelihood":0.40,"impact_min":1_000_000,"impact_max":5_000_000},{"name":"Ransomware","likelihood":0.15,"impact_min":10_000_000,"impact_max":50_000_000},{"name":"Insider","likelihood":0.10,"impact_min":5_000_000,"impact_max":20_000_000},]

controls = [{"id":"mfa","cost":200000,"risk_reduction":0.15},{"id":"edr","cost":500000,"risk_reduction":0.30},{"id":"patch","cost":100000,"risk_reduction":0.10},{"id":"backup","cost":300000,"risk_reduction":0.20},{"id":"training","cost":50000,"risk_reduction":0.08},]

# ---------- Main ----------
budget = 1_000_000
before = simulate_risk(events)
reduction, selected = optimize_budget(budget, controls)
reduced_events = []
for e in events:
    reduced_events.append({**e,"likelihood": e["likelihood"] * (1 - reduction)})
after = simulate_risk(reduced_events)
print("\n=== HEXCELL MVP ===")
print("Selected Controls:", selected)
print(f"Combined Risk Reduction: {reduction*100:.2f}%")
print("\nBefore Investment")
print(f"Expected Loss: ₹{before['expected_loss']:,.0f}")
print(f"P50 Loss: ₹{before['p50_loss']:,.0f}")
print(f"P95 Loss: ₹{before['p95_loss']:,.0f}")
print("\nAfter Investment")
print(f"Expected Loss: ₹{after['expected_loss']:,.0f}")
print(f"P50 Loss: ₹{after['p50_loss']:,.0f}")
print(f"P95 Loss: ₹{after['p95_loss']:,.0f}")
