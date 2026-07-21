# Changelog

All notable changes to this project are documented here.

## 1.1.0 — 2026-07-21

- Added mandatory reproducibility snapshots with exact revisions, real repository paths, evidence commands, and tool context.
- Added mechanism-identity checks so independently configured producers, transports, consumers, and acknowledgement paths are not conflated.
- Added execution-path verification for synchronous calls, retries, swallowed exceptions, compensation, reconciliation direction, feature flags, and compatibility fallbacks.
- Added explicit storage-role classification for live state, rollback evidence, checkpoints, audit history, source observations, and derived caches.
- Added a per-handler retry, replay, redelivery, and dead-letter safety gate covering idempotency, deduplication, error propagation, and progress accounting.
- Added verification rules for quantitative claims, source-file versus runtime-unit counts, version-control provenance, inherited build configuration, and legacy behavior.
- Replaced impressionistic maturity ranges with a six-dimension rubric; unsupported ratings must be reported as `NOT RATED`.
- Added an evaluation mode with `USEFUL`, `NEUTRAL`, `HARMFUL`, and `UNKNOWN` classifications, counterfactual requirements, hard guardrails, a JSON Schema run contract, and a deterministic JSONL summarizer.
- Expanded review templates, strict artifact validation, package validation, release contents, and tests to enforce the new requirements.

## 1.0.0 — 2026-07-21

- Initial dual-compatible Codex and Claude Code plugin.
- Added the `align-system` Agent Skill with design, review, planning, repair, implementation, and operations modes.
- Added a normative system-reality alignment standard, evidence model, stage-specific procedures, artifact templates, and deterministic local scripts.
- Added package and artifact validation with unit tests.
- Added public Codex and Claude Code marketplace installation metadata and maintainer links.
- Added deterministic platform-specific release archives, extracted-archive validation, and SHA-256 checksums.
- Hardened GitHub Actions and added contributor, issue, pull-request, and private vulnerability-reporting guidance.
