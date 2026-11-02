from pathlib import Path

from agentfault.runner.engine import run_scenario
from agentfault.scenarios import load_scenarios

root = Path(__file__).resolve().parents[1]
scenarios = load_scenarios(root / "scenarios")
scenario = scenarios["order_malformed_response"]

for policy in ("none", "retry", "state_aware"):
    result = run_scenario(scenario, policy)
    print({
        "policy": policy,
        "success": result.success,
        "updates": result.final_state.get("orders", {}).get("order-1", {}).get("updates"),
        "violations": len(result.invariant_violations),
        "retries": result.retries,
    })
