**Why CUPED?** Pre-period engagement is correlated with the outcome, so CUPED lowers estimator variance while preserving the randomized estimand. I keep the raw estimate for comparison and auditability.

**Why not just trust the p-value?** A p-value does not encode practical significance, safety, latency, unit economics, or heterogeneous harm. Those are product criteria and appear explicitly in the decision policy.

**What would change in production?** I would add pre-experiment power analysis, sample-ratio-mismatch checks, exposure logging, sequential-testing controls, experiment health alerts, metric lineage, and a durable warehouse model.

**How would this work for a marketplace?** Randomization may create interference. I would consider switchback, geo, or cluster randomization; model supply-side outcomes; and use cluster-robust inference.

**How would this work for an AI assistant?** I would add task-level quality rubrics, evaluator calibration against human labels, prompt/model version lineage, abuse slices, and a long-horizon retention read.

## Strong extensions

1. Add a power and minimum-detectable-effect planner.
2. Implement sequential confidence sequences or alpha spending.
3. Add doubly robust heterogeneous treatment-effect estimation.
4. Back the API with DuckDB and dbt-style metric definitions.
5. Add OpenTelemetry traces and a model/prompt experiment registry.

## Honest boundaries

The data is synthetic. Say this immediately. The project demonstrates experimental reasoning, system design, implementation quality, and product judgment—not a claim that a simulated lift is a business result.

