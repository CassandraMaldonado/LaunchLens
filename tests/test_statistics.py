import numpy as np
import pytest

from launch_lens.simulation import simulate_experiment
from launch_lens.statistics import benjamini_hochberg, cuped_adjust, estimate_effect


def test_simulation_is_deterministic_and_balanced():
    first = simulate_experiment(2_000, seed=7)
    second = simulate_experiment(2_000, seed=7)
    assert np.array_equal(first.engagement, second.engagement)
    assert 0.46 < np.mean(first.treatment) < 0.54


def test_cuped_preserves_mean_and_reduces_variance():
    data = simulate_experiment(8_000, seed=9)
    adjusted, theta = cuped_adjust(data.engagement, data.pre_engagement)
    assert np.mean(adjusted) == pytest.approx(np.mean(data.engagement))
    assert theta > 0
    assert estimate_effect(adjusted, data.treatment).standard_error < estimate_effect(data.engagement, data.treatment).standard_error


def test_effect_recovery_and_segment_heterogeneity():
    data = simulate_experiment(30_000, seed=11)
    overall = estimate_effect(data.engagement, data.treatment)
    power = data.segment == "power"
    power_effect = estimate_effect(data.engagement[power], data.treatment[power])
    assert 0.2 < overall.absolute_effect < 0.6
    assert power_effect.absolute_effect < 0


def test_benjamini_hochberg_is_monotonic_in_rank():
    raw = [0.04, 0.001, 0.03, 0.6]
    adjusted = benjamini_hochberg(raw)
    ordered = sorted(zip(raw, adjusted))
    assert all(ordered[i][1] <= ordered[i + 1][1] for i in range(len(ordered) - 1))
    assert all(a >= p for p, a in zip(raw, adjusted))
