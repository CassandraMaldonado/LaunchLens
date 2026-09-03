"""Small, inspectable statistical primitives used by the decision engine."""

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class Estimate:
    control_mean: float
    treatment_mean: float
    absolute_effect: float
    relative_effect: float
    ci_low: float
    ci_high: float
    p_value: float
    standard_error: float
    n_control: int
    n_treatment: int


def cuped_adjust(outcome: np.ndarray, pre_period: np.ndarray) -> tuple[np.ndarray, float]:
    """Adjust an outcome using a centered pre-treatment covariate."""
    variance = np.var(pre_period, ddof=1)
    theta = 0.0 if variance == 0 else float(np.cov(outcome, pre_period, ddof=1)[0, 1] / variance)
    adjusted = outcome - theta * (pre_period - np.mean(pre_period))
    return adjusted, theta


def estimate_effect(outcome: np.ndarray, treatment: np.ndarray) -> Estimate:
    control = np.asarray(outcome)[~treatment]
    treated = np.asarray(outcome)[treatment]
    effect = float(np.mean(treated) - np.mean(control))
    se = float(np.sqrt(np.var(control, ddof=1) / len(control) + np.var(treated, ddof=1) / len(treated)))
    dof_numerator = (np.var(control, ddof=1) / len(control) + np.var(treated, ddof=1) / len(treated)) ** 2
    dof_denominator = (
        (np.var(control, ddof=1) / len(control)) ** 2 / (len(control) - 1)
        + (np.var(treated, ddof=1) / len(treated)) ** 2 / (len(treated) - 1)
    )
    dof = dof_numerator / dof_denominator
    critical = float(stats.t.ppf(0.975, dof))
    p_value = float(2 * stats.t.sf(abs(effect / se), dof)) if se else 1.0
    control_mean = float(np.mean(control))
    return Estimate(
        control_mean=control_mean,
        treatment_mean=float(np.mean(treated)),
        absolute_effect=effect,
        relative_effect=effect / control_mean if control_mean else 0.0,
        ci_low=effect - critical * se,
        ci_high=effect + critical * se,
        p_value=p_value,
        standard_error=se,
        n_control=len(control),
        n_treatment=len(treated),
    )


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    """Return monotonic false-discovery-rate adjusted p-values."""
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    ranked = values[order]
    adjusted_ranked = ranked * len(values) / np.arange(1, len(values) + 1)
    adjusted_ranked = np.minimum.accumulate(adjusted_ranked[::-1])[::-1]
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = np.minimum(adjusted_ranked, 1.0)
    return adjusted.tolist()

