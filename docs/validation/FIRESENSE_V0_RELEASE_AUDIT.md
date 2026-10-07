# FireSense v0 Release Audit

Generated: 2026-10-07T18:24:36.171146+00:00

## Software status

- Implementation roadmap: Steps 1-200 completed.
- Backend regression target: all tests passing.
- OpenAPI contract regenerated from the current application.
- Frontend generated API types must match the frozen OpenAPI contract.
- Frontend typecheck, lint and production build must pass.

## Scientific release status

- Independent external comparison evidence: available.
- Independent external validation: not yet established.
- Production-ready scientific claim: not allowed.
- Certification claim: not allowed.

This status is intentional and fail-closed.

FireSense v0 must not be described as independently externally validated
until a real compatible holdout dataset passes provenance, compatibility,
performance, calibrated uncertainty coverage, scientific review and
SHA-bound release promotion.

## Current scientific scope

- Material: PMMA
- Geometry family: thin sheet
- Oxygen: 21%
- Pressure: approximately 101.325 kPa
- Reduced-gravity reference transport: opposed flow
- Reference opposed-flow velocity: 50 mm/s
- Primary modeled quantity: flame spread rate

## Frozen artifact integrity

### OpenAPI

- Path: `docs\api\openapi.json`
- SHA-256: `afcf64877fd53dd89d8b4cf4c1e3cbca2e50f9057700ba16a50e90b15e93f015`

### Baseline dataset

- Path: `data\curated\thin_sheet\baseline_dataset_v0.jsonl`
- SHA-256: `4024475ca9f0bf5d703ce1cb375e6d9e11897ead4dfc3f5e0fe6369879798ab4`

### Figure 2.22 dataset

- Path: `data\curated\thin_sheet\figure_2_22_comparison_dataset_v0.jsonl`
- SHA-256: `ee7e7d54b57e2bdcbd9dd4eddbcdf8b9ad88b9924fcee31a4ad7ddac3aff2a9d`

### Validation acceptance criteria

- Path: `data\manifests\independent_validation_acceptance_criteria_v0.json`
- SHA-256: `a3c7a88c3ad52efbb2a3170fd67d5d9219bb25ac7325f3950954dd8962c9e783`

### Validation performance protocol

- Path: `data\manifests\independent_validation_performance_acceptance_v0.json`
- SHA-256: `bde2263ea33687d21c4dbbd0f98e567f20ba4c2809697304f11476b5dae37573`

### Validation source registry

- Path: `data\manifests\independent_validation_source_registry_v0.json`
- SHA-256: `c6302ad47feb44c71a101c14871d76b30db69e5fd1db3d67b3fb8fd45f933ceb`

## Release guardrails

- Physics/statistical code produces numeric model output.
- Language-model explanation must not invent numerical science.
- Comparison evidence must not be labelled validation.
- Theory/computation must not contaminate experimental training rows.
- Validation evidence remains holdout and training-ineligible.
- Experimental, digitization and model uncertainty remain separate.
- Current residual factors are not calibrated confidence intervals.
- Unsupported conditions must abstain rather than extrapolate silently.
- Scientific validation does not imply certification.
- Scientific validation does not automatically imply production readiness.

## Outstanding scientific blocker

A real independent experimental dataset matching the declared validation
domain has not yet been approved and installed.

The preferred validation evidence remains an independent PMMA thin-sheet
true-microgravity dataset near 200 ?m, 21% O2, approximately 1 atm and
50 mm/s opposed flow, with at least three independent numeric
flame-spread observations and preserved uncertainty/provenance metadata.
