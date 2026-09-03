# Methodology

## Estimand

The primary estimand is the intention-to-treat difference in meaningful sessions per randomized user. Randomization is simulated at the user level with approximately equal allocation.

## CUPED

The primary outcome is adjusted with pre-period engagement:

`Y_adjusted = Y - theta * (X_pre - mean(X_pre))`

where `theta = cov(Y, X_pre) / var(X_pre)`. Because the covariate is measured before assignment, it improves precision without controlling for a post-treatment mediator. The unadjusted estimate remains in the API response for auditability.

## Inference

LaunchLens uses a two-sided Welch t-test and a 95% confidence interval. This is appropriate for the continuous synthetic outcome and unequal group variances. In production I would pre-register the estimand, power the test against a minimum detectable effect, validate sample-ratio mismatch, and use cluster-robust or randomization-based inference if assignment were clustered.

## Heterogeneous effects

Effects are estimated separately for new, casual, and power users. Reported subgroup p-values use Benjamini–Hochberg false-discovery-rate adjustment. Segment findings remain exploratory unless the analysis plan pre-specified them.

## Decision policy

Statistical significance is evidence, not a decision. The policy requires a credible and practically meaningful primary win, then checks AI quality, latency, safety, unit economics, and credible subgroup harm. Thresholds are visible in the API response and dashboard.

## Known limitations

- Synthetic data is useful for demonstrating design and engineering, but does not reproduce every production failure mode.
- Normal approximations are imperfect for rare safety events; an exact or Bayesian interval would be preferable.
- The economic model uses a transparent proxy value, not a causal estimate of long-term revenue.
- Novelty effects and interference are encoded only lightly; a long-running test and network-aware design may be required.

