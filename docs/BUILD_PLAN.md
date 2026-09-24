# Build plan: 23 Sep → 7 Oct 2026

Goal for 7 October: the partner types any practice code into the admin page and gets that practice's
dashboard, built from real July 2026 data, with every number real or absent. Fallback: the same pages
pre-built as static HTML.

Each step below is one Claude Code session. Paste the prompt as it is. Each step ends with a checkpoint
you verify yourself. Don't start the next step until the checkpoint passes.

**Rule for every session:** start with "Read CLAUDE.md and docs/BUILD_PLAN.md step N first."

---

## Step 0 — Repo set-up (Wed 23 Sep, 30 min)

```
Read CLAUDE.md. Set up this repo: git init, Python 3.12 project with pyproject.toml (duckdb, pyarrow,
pydantic>=2, pyyaml, jsonschema, httpx, pytest, ruff), a Makefile with targets `fixture`, `lint`, `static`,
`test`, and a GitHub Actions workflow running ruff + pytest + `python tools/lint_payload.py payloads/*.json`.
Add a test that builds the fixture payload, validates it against the schema, and runs the linter.
Don't change web/app.html or the schema.
```
**Checkpoint:** `make fixture static` produces `dist/E84000.html`, which opens and matches the v9 prototype.

---

## Step 1 — Data inventory (Wed 23 – Thu 24 Sep) ← the most important step

Put the real downloaded files in `data/raw/<source>/<period>/`. Then:

```
Read CLAUDE.md and registry/metrics.yaml. For every file under data/raw/, write a profiling script
(tools/profile_source.py) that prints: row count, columns with dtype and 3 example values, the practice
identifier column, period columns, and every distinct value of any column with < 50 distinct values
(these are the breakdown dimensions). Write the results to docs/inventory/<source>.md.

Then write docs/inventory/SUMMARY.md with one table:
source | grain | period covered | practice id column | breakdowns available AT PRACTICE LEVEL | refresh | notes.

Then answer these questions explicitly, with evidence from the files:
1. Telephony: which fields give inbound, answered, abandoned, callback requested/completed, wait bands?
   Is answered + abandoned + other = inbound? Is there an hourly or weekday breakdown per practice?
2. Does 'waited 5+ min' use answered calls as its denominator? Recompute it for practice <ODS> and show the arithmetic.
3. GPAD: which fields carry the 2026/27 access measures (urgent same day, routine ≤7/≤14 days)?
   Which breakdowns exist per practice (HCP type, mode, time between booking and appointment, weekday)?
4. Workforce: what FTE definitions exist for GPs (all GPs, fully qualified, excluding trainees)? What cadence?
Update registry/metrics.yaml: replace `fields: TBD` with real column names where confirmed; add
`open_question` where not. Do not invent fields.
```
**Checkpoint:** you read SUMMARY.md and can answer: which L2/L3 visuals in the prototype are impossible with
public data? Mark them in `docs/DESIGN_V9.md` → "Dropped for lack of data".

---

## Step 2 — Ingest to canonical observations (Thu 24 – Fri 25 Sep)

```
Read CLAUDE.md (canonical observation table) and docs/inventory/SUMMARY.md. Implement
pipeline/ingest/<source>.py for: ods, reg, cbt, gpad, ocs, gpps. Each parser: reads raw files for a period,
normalises field names, emits rows to data/obs/observations.parquet via DuckDB, stamps source_version.
Observations are append-only; re-running is idempotent (same source_version = no new rows).
pipeline/ingest/ods.py builds an effective-dated mapping table practice→PCN→ICB.
Each parser gets a fixture test using a 20-row sample of the real file saved under tests/fixtures/.
Add `make ingest PERIOD=2026-07`.
```
**Checkpoint:** a DuckDB query returns all of one practice's July observations across sources, and row counts
match the raw files.

---

## Step 3 — Metrics from the registry (Sat 26 – Sun 27 Sep)

```
Read CLAUDE.md and registry/metrics.yaml. Implement pipeline/metrics.py: load the registry, compute every
metric with validation != 'blocked' for every practice for a period, write data/metrics/<period>.parquet
with columns ods_code, metric_id, period, value, numerator, denominator, suppressed(bool), dims(json).
Apply min_denominator suppression. Implement the `reconcile_with` check and write failures to
data/metrics/<period>_qa.parquet. Tests: for one real practice, a hand-calculated expected value per metric
(I will supply these). Metrics code must read formulas/fields from the registry — no metric-specific
if/else chains outside a small, documented set of formula kinds.
```
**Checkpoint:** you check 3 practices by hand against the raw files, for the Contact & Access metrics.
This is where the 1,013 vs 4,570 contradiction gets resolved.

---

## Step 4 — Comparators and rules (Mon 28 – Tue 29 Sep)

```
Read CLAUDE.md and the `rules` section of registry/metrics.yaml. Implement:
- pipeline/comparators.py: per metric, PCN rank (1 = best, respecting direction), ICB median/P20/P80,
  England median, own trend (last 3/6/12 points), using the effective-dated ODS mapping.
- pipeline/rules.py: status per metric and per area (area status = worst metric status that has real data),
  materiality for What Changed, priority score per area, attention selection (highest priority),
  assessment lines (top 3 areas by priority, status copied from the area).
- Findings are structured objects {area, kind: association|observed, template_id, params}; text is rendered
  from templates in pipeline/templates/findings.yaml. No free-text generation of numbers.
Write unit tests for every rule with small synthetic inputs, including: status never says 'breach' for a
benchmark; attention points at max priority; What Changed returns 0 items when nothing is material.
```
**Checkpoint:** the rules output for Kilburn Park reads true to you and your partner.

---

## Step 5 — Payload generation (Wed 30 Sep)

```
Read CLAUDE.md, schema/payload.schema.json and payloads/build_demo_payload.py (fixture, for shape).
Implement pipeline/payload.py: build one payload per practice from metrics + comparators + rules, using
pydantic models generated from the schema. Only the Contact & Access area and the access-measure strip are
fully populated; other areas use status 'unable' with no figures until their metrics exist.
Every value has prov='real'. Emit payloads/2026-07/<ODS>.json for all practices, validate each against
the schema, run tools/lint_payload.py on all of them, and print a summary: how many pass, and the
most common lint errors. `make payloads PERIOD=2026-07`.
```
**Checkpoint:** `python tools/build_static.py payloads/2026-07/<ODS>.json --demo` for 5 practices you know.
The vertical slice is done here.

---

## Step 6 — Breadth: remaining areas (Wed 30 Sep – Fri 2 Oct)

One session per area, same pattern: registry entries → metrics → rules → payload section.
Order by data readiness: **Missed appointments** (GPAD) → **Appointment access** (GPAD) →
**Workforce & capacity** (WF + reg; decide the GP FTE denominator first) → **QOF** (points not achieved;
annual) → **Patient experience** (GPPS; paired with operational findings).
**Prevention stays `in_development`** for the demo.

```
Read CLAUDE.md. Add the <AREA> area end to end: registry entries (confirm fields from docs/inventory),
metrics, status/priority rules, L2 'what/where/investigate/ai/evidence', and only the L3 tabs the data
supports (list the tabs you dropped and why in docs/DESIGN_V9.md). Tests as in steps 3–4.
```

---

## Step 7 — Validation with real practices (Thu 1 – Fri 2 Oct)

Not a coding step. Your partner takes 3–5 practice managers through their own page. Log each disagreement
as an issue: metric id, practice, what they expected, what we showed. Fix before Step 9.

---

## Step 8 — Admin portal (Sat 3 – Mon 5 Oct)

```
Read CLAUDE.md. Build a minimal admin app: FastAPI serving /login (single shared credential from env,
bcrypt-hashed, session cookie), /practice?code=<ODS> which returns dist-style HTML rendered from
payloads/<period>/<ODS>.json via the same web/app.html template (no second renderer), and a search box
by practice name or ODS code. No payload is served without login. Dockerfile; deploy target: <your host>.
Log every practice view (who/when/code) for demo follow-up.
```
Fallback in the same session: `make static-all PERIOD=2026-07 PRACTICES=<list>` builds demo-mode HTML for
the practices the partner expects to meet.

---

## Step 9 — Freeze and rehearse (Tue 6 Oct)

- Rebuild all payloads from a clean checkout; lint must report zero errors.
- Open the 10 practices most likely to be looked up; check every number shown against the raw files.
- Put the static fallback on a USB stick and on the partner's laptop.
- Default mode on the admin portal = "Real data only". The placeholder toggle is for internal use.

---

## After 7 October

Demo feedback → scope. Parked: Prevention method, peer-group definition for "similar practices",
full L3 tab set, QOF monetary value, PCN product, V2 enrichment (Open Exeter, telephony exports).
