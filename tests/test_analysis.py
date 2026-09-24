# Test to make sure the full analysis produces a reasonable decision brief. 
# It checks the decision options, confidence
# interval, segment results, guardrails, and the expected benefit from CUPED.

from launch_lens.analysis import analyze_experiment
from launch_lens.simulation import simulate_experiment


def test_analysis_contract_and_policy():
    result = analyze_experiment(simulate_experiment(12_000, seed=42))
    assert result["decision"]["status"] in {"SHIP", "ITERATE", "HOLD"}
    assert result["primary_metric"]["ci_low"] < result["primary_metric"]["absolute_effect"] < result["primary_metric"]["ci_high"]
    assert len(result["segments"]) == 3
    assert len(result["guardrails"]) == 4
    assert result["methodology"]["variance_reduction"] > 0

