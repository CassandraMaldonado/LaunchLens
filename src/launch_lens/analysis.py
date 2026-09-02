"""Experiment analysis and explicit product decision policy."""

from dataclasses import asdict
from typing import Any

import numpy as np

from .simulation import SEGMENTS, ExperimentData
from .statistics import benjamini_hochberg, cuped_adjust, estimate_effect


def _estimate_dict(outcome: np.ndarray, treatment: np.ndarray) -> dict[str, Any]:
    return asdict(estimate_effect(outcome, treatment))


def analyze_experiment(data: ExperimentData) -> dict[str, Any]:
    adjusted_engagement, theta = cuped_adjust(data.engagement, data.pre_engagement)
    primary = _estimate_dict(adjusted_engagement, data.treatment)
    raw = _estimate_dict(data.engagement, data.treatment)
    retention = _estimate_dict(data.retained, data.treatment)
    quality = _estimate_dict(data.quality, data.treatment)
    latency = _estimate_dict(data.latency_ms, data.treatment)
    safety = _estimate_dict(data.safety_flag, data.treatment)
    cost = _estimate_dict(data.cost_usd, data.treatment)

    segment_results = []
    for segment in SEGMENTS:
        mask = data.mask(str(segment))
        estimate = _estimate_dict(adjusted_engagement[mask], data.treatment[mask])
        segment_results.append({"segment": str(segment), **estimate})
    adjusted_p = benjamini_hochberg([row["p_value"] for row in segment_results])
    for row, p_value in zip(segment_results, adjusted_p, strict=True):
        row["adjusted_p_value"] = p_value

    variance_reduction = 1 - primary["standard_error"] ** 2 / raw["standard_error"] ** 2
    incremental_engagement_value = primary["absolute_effect"] * 0.035
    net_value_per_user = incremental_engagement_value - cost["absolute_effect"]

    guardrails = [
        _guardrail("AI quality", quality["absolute_effect"] >= 0.03, quality["absolute_effect"], ">= +0.03"),
        _guardrail("Latency", latency["absolute_effect"] <= 175, latency["absolute_effect"], "<= +175 ms"),
        _guardrail("Safety flags", safety["absolute_effect"] <= 0.005, safety["absolute_effect"], "<= +0.50 pp"),
        _guardrail("Unit economics", net_value_per_user > 0, net_value_per_user, "> $0 / user"),
    ]

    significant_win = primary["ci_low"] > 0 and primary["relative_effect"] >= 0.04
    failed = [item for item in guardrails if not item["passed"]]
    harmed_segments = [row["segment"] for row in segment_results if row["ci_high"] < 0]
    if significant_win and not failed and not harmed_segments:
        decision = "SHIP"
    elif primary["ci_high"] <= 0 or len(failed) >= 2:
        decision = "HOLD"
    else:
        decision = "ITERATE"

    reasons = [
        f"Engagement changed {primary['relative_effect']:+.1%} (95% CI {primary['ci_low']:+.2f} to {primary['ci_high']:+.2f}).",
        f"CUPED reduced estimator variance by {variance_reduction:.1%}.",
        f"Estimated net value is ${net_value_per_user:+.3f} per exposed user.",
    ]
    risks = [f"{item['name']} missed its launch threshold." for item in failed]
    risks += [f"Credible engagement harm detected for the {segment} segment." for segment in harmed_segments]
    if not risks:
        risks.append("No launch-blocking guardrail or segment harm detected; continue post-launch monitoring.")

    return {
        "experiment": {
            "name": "AI Discovery Assistant",
            "hypothesis": "Guided discovery increases meaningful engagement without unacceptable quality, safety, latency, or cost regressions.",
            "users": len(data.user_id),
            "treatment_share": float(np.mean(data.treatment)),
        },
        "decision": {"status": decision, "reasons": reasons, "risks": risks},
        "primary_metric": {"name": "Meaningful sessions / user", **primary},
        "raw_primary_metric": raw,
        "secondary_metrics": {"retention": retention, "quality": quality, "latency_ms": latency, "safety_rate": safety, "cost_usd": cost},
        "segments": segment_results,
        "guardrails": guardrails,
        "economics": {"incremental_value_per_user": incremental_engagement_value, "incremental_cost_per_user": cost["absolute_effect"], "net_value_per_user": net_value_per_user},
        "methodology": {"cuped_theta": theta, "variance_reduction": variance_reduction, "confidence_level": 0.95, "multiplicity_control": "Benjamini-Hochberg FDR"},
    }


def _guardrail(name: str, passed: bool, observed: float, threshold: str) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "observed": float(observed), "threshold": threshold}

