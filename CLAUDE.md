# Practice Intelligence — instructions for Claude Code

GP Practice Intelligence for English NHS practices. It tells a practice manager what matters,
why, where to look, and how they compare. Public aggregate data only: no patient-level data
and no clinical-system integration.

**Deadline that drives everything:** conference demo on **7 October 2026**. Every number shown
on that day is real or absent.

## How the system fits together

```
data/raw/<source>/<period>/*        downloaded NHS files, never edited
      │  pipeline/ingest/<source>.py      one parser per source, deterministic
      ▼
data/obs/observations.parquet       canonical long table (see below)
      │  pipeline/metrics.py              reads registry/metrics.yaml, computes every metric for every practice
      ▼
data/metrics/<period>.parquet       practice × metric × period, with numerator/denominator
      │  pipeline/comparators.py          PCN rank, ICB median, England, own trend, peer group
      │  pipeline/rules.py                status, assurance, materiality, priority score, findings
      ▼
payloads/<period>/<ODS>.json        one file per practice; validates against schema/payload.schema.json
      │  tools/build_static.py            inlines payload into web/app.html
      ▼
dist/<ODS>.html                     static page (conference fallback), or served by the admin portal
```

The renderer (`web/app.html`) **never calculates**. If a number needs working out, it belongs in the pipeline.

## Non-negotiable rules

1. **Registry first.** A metric does not exist until it is in `registry/metrics.yaml` with source, fields, formula,
   denominator, period grain, directionality, comparators, assurance class and validation status. Code reads the
   registry; it never hard-codes a formula that isn't there.
2. **Assurance comes from the registry, never from copy.** The five classes are `contract_requirement`,
   `national_ambition`, `qof_threshold`, `local_expectation`, `benchmark`. Never produce text that implies
   below-benchmark = breach, or below-ambition = contractual non-compliance.
3. **Provenance on every value.** Every `val` in the payload is `real` or `illustrative`. The pipeline only emits `real`.
   `illustrative` exists for fixtures and must never reach a practice.
4. **Associations are not causes.** Cross-dataset relationships are investigation triggers. Language: "tend to",
   "goes with", "no relationship found". Never "ruled out", "caused by", "because".
5. **No fake conversions.** Calls and appointments come from different datasets with no patient linkage. Never compute
   "call to appointment conversion".
6. **Denominators reconcile.** If two figures on the same page imply different denominators, `qa` gets an `error`
   and the payload is not demo-ready. (Example: 1,013 calls at 35.8% implies 2,830 answered; outcomes said 4,570.)
7. **Don't pad.** What Changed shows 0–3 items that pass materiality rules. The attention panel points at the
   highest-priority area. `tools/lint_payload.py` enforces both.
8. **Effective-dated mappings.** Practice → PCN → ICB membership changes (mergers, closures). Always join on the
   mapping valid for the period, never "latest".
9. **Small numbers.** Suppress any rate with a denominator below the registry's `min_denominator`; render as "too few".

## Canonical observation table

| column | type | notes |
|---|---|---|
| ods_code | str | practice code, `^[A-Z][0-9]{5}$` |
| period_start / period_end | date | month for GPAD/telephony; financial year for QOF; survey year for GPPS |
| source | str | e.g. `gpad`, `cbt`, `ocs`, `gpps`, `qof`, `wf`, `reg`, `imd`, `ods` |
| source_version | str | file name + publication date; observations are immutable, re-publications add rows |
| field | str | raw field name after normalisation |
| dims | json | breakdowns, e.g. `{"hcp_type":"GP","time_between":"Same day"}` |
| value | float | |
| loaded_at | timestamp | |

## Conventions

- Python 3.12, DuckDB + Parquet, pydantic for payload models, pytest. No pandas in hot paths if DuckDB SQL is clearer.
- Every parser has a fixture test using a 20-row sample of the real file in `tests/fixtures/`.
- Every metric has a test with a hand-calculated value for one real practice.
- `make demo` = ingest → metrics → comparators → rules → payloads → lint → static build.
- Display strings are formatted in the pipeline (`"35.8%"`, `"6m 40s"`, `"2,196"`), British English, en-GB number format.
- Copy: short, plain, readable by a receptionist. No percentiles on L1. No jargon without a tooltip.

## Where things are

- `web/app.html` — renderer (L1 overview, L2 drawer, L3 wide drawer). Chart components take a `block` spec.
- `schema/payload.schema.json` — the contract between engine and renderer. Change it deliberately, bump `schema_version`.
- `payloads/build_demo_payload.py` — fixture payload (Kilburn Park, v8 content). Reference for shape, not for numbers.
- `registry/metrics.yaml` — metric registry, Contact & Access first.
- `tools/lint_payload.py` — product-rule checks. Must pass before any payload is shown to anyone.
- `docs/BUILD_PLAN.md` — the 14-day plan with the prompt for each step.
- `docs/DESIGN_V9.md` — what changed from v8 and why.

## Working style

- The product owner validates numbers against real practices; that is the bottleneck, not code. Surface anything
  that needs a human check as a `qa` item instead of guessing.
- Before writing a parser, open the real file and print its columns and 5 rows. Never assume a schema.
- When a public dataset lacks a breakdown the design wants (e.g. urgent same-day by weekday at practice level),
  say so and drop the visual. Do not approximate it.
