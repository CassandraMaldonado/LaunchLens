"""Reproducible, event-level AI product experiment simulation."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ExperimentData:
    user_id: np.ndarray
    treatment: np.ndarray
    segment: np.ndarray
    pre_engagement: np.ndarray
    engagement: np.ndarray
    retained: np.ndarray
    quality: np.ndarray
    latency_ms: np.ndarray
    safety_flag: np.ndarray
    cost_usd: np.ndarray

    def mask(self, segment: str | None = None) -> np.ndarray:
        return np.ones(len(self.user_id), dtype=bool) if segment is None else self.segment == segment


SEGMENTS = np.array(["new", "casual", "power"])


def simulate_experiment(n_users: int = 12_000, seed: int = 42) -> ExperimentData:
    """Simulate a randomized test with realistic heterogeneous treatment effects."""
    if n_users < 200:
        raise ValueError("n_users must be at least 200 for stable experiment diagnostics")

    rng = np.random.default_rng(seed)
    segment = rng.choice(SEGMENTS, n_users, p=[0.34, 0.46, 0.20])
    treatment = rng.integers(0, 2, n_users).astype(bool)
    baseline = np.select([segment == "new", segment == "casual"], [2.4, 4.8], default=8.2)
    user_affinity = rng.normal(0, 1.15, n_users)
    pre_engagement = np.maximum(0, baseline + user_affinity + rng.normal(0, 1.1, n_users))

    # The assistant helps new/casual users discover content, but initially distracts power users.
    treatment_effect = np.select(
        [segment == "new", segment == "casual"], [0.72, 0.42], default=-0.18
    )
    engagement = np.maximum(
        0,
        baseline + 0.72 * user_affinity + treatment * treatment_effect + rng.normal(0, 1.45, n_users),
    )
    retention_logit = -1.5 + 0.28 * engagement + treatment * 0.10
    retained = rng.random(n_users) < (1 / (1 + np.exp(-retention_logit)))

    quality = np.clip(0.75 + treatment * 0.075 + rng.normal(0, 0.09, n_users), 0, 1)
    latency_ms = np.maximum(80, rng.lognormal(np.log(310 + treatment * 135), 0.24, n_users))
    safety_probability = 0.008 + treatment * 0.0025 + (segment == "new") * 0.001
    safety_flag = rng.random(n_users) < safety_probability
    cost_usd = np.maximum(0.001, 0.006 + treatment * rng.gamma(2.2, 0.008, n_users))

    return ExperimentData(
        user_id=np.arange(1, n_users + 1),
        treatment=treatment,
        segment=segment,
        pre_engagement=pre_engagement,
        engagement=engagement,
        retained=retained.astype(float),
        quality=quality,
        latency_ms=latency_ms,
        safety_flag=safety_flag.astype(float),
        cost_usd=cost_usd,
    )

