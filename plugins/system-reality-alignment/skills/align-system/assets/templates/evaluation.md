# {{SYSTEM_NAME}} — Intervention Evaluation

**Date:** {{DATE}}  
**Mode:** Evaluation  
**Status:** Draft

## Executive Decision

**Classification:** UNKNOWN

## Evaluation Question and Eligible Population

- **Evaluation ID:**

## Intervention and Version Snapshot

- **Intervention:**
- **Plugin/intervention version under evaluation (same value in control and treatment records):**
- **Model and tool versions:**
- **Repository revision:**
- **Evaluation period:**

## Segments and Exclusions

## Counterfactual and Assignment

- **Design:** randomized live | randomized shadow | historical replay | matched control | time series | weak before/after
- **Unit of assignment:**
- **Assignment method:**
- **Assignment versus activation handling:**
- **Reviewer blinding or independent outcome source:**

## Primary Metric and Equivalence Band

- **Primary metric:**
- **Direction:** higher is better | lower is better
- **Minimum practically meaningful effect (delta):**
- **Observation window:**
- **Outcome maturity rule:**
- **Minimum mature observations per arm:**

## Guardrails and Stop Conditions

- **Hard guardrails:**
- **Treatment-arm classification rule:** Any treatment-arm hard guardrail event conservatively classifies the segment as `HARMFUL`.
- **Control-arm handling:** Report control-arm events separately as baseline risk; they do not by themselves classify the intervention as harmful, but may invalidate causal interpretation.
- **Stop conditions:**

## Data Quality and Outcome Maturity

- **Outcome maturity:**
- **Independent outcome source:**
- **Missingness and exclusions:**
- **Assignment contamination or non-compliance:**

## Results by Segment

| Segment | Control n | Treatment n | Control result | Treatment result | Normalized effect | Uncertainty interval | Outcome mature | Guardrails C/T | Classification |
|---|---:|---:|---:|---:|---:|---|---|---:|---|

## Guardrail Events and Failure Modes

Separate control-arm baseline events from treatment-arm events. Record evidence, attribution limits, and any effect on evaluation validity.

## Classification

Use exactly one status per segment: `USEFUL`, `NEUTRAL`, `HARMFUL`, or `UNKNOWN`.

## Cost and Workflow Impact

## Rollout, Restriction, or Kill-Switch Decision

## Residual Uncertainty and Next Review
