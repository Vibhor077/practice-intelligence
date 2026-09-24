# Prototype v9: what changed from v8, and why

The v8 information architecture (L1/L2/L3, groups, visual grammar) is kept exactly as frozen on 22 Sep.
v9 fixes consistency and honesty problems, and splits data from rendering so the pipeline can drive it.

## Structural

| v8 | v9 | Why |
|---|---|---|
| Data hard-coded in the page's script (`A`, `contract`, `changed`) | One JSON payload per practice, validated by `schema/payload.schema.json` | The engine produces payloads; the page only renders. The same file serves the admin portal and the static fallback. |
| Placeholder toggle on/off | **Show placeholders / Real data only** | Real-data-only hides every placeholder and marks areas without real figures "Unable to assess". This is the demo mode. |
| No checks on the page itself | **Data checks** panel (placeholder mode only) | The run's QA items: denominators that don't reconcile, suspicious jumps, held-back methods. |

## L1

| v8 | v9 | Why |
|---|---|---|
| Attention panel = urgent same-day (Watch, placeholder number) | Attention panel = **telephone waiting** (Attention, real, highest priority) with a "why this is first" row | The most prominent element contradicted the status system and the assessment. The linter now enforces "attention = highest priority". |
| Assessment icons disagreed with area status (QOF Attention shown ✓) | Icon = the area's status; each line opens its area | Linter check 3. |
| Header showed Patients per GP | Header: patients, IMD decile, 60+, data period. Sub-line adds ODS code | Per 22 Sep report. Patients per GP moved into Workforce & capacity. |
| What Changed: always 3 | 0–3 items, with the comparison basis stated. "Appointments ▲25%" carries a **Verify** flag | Don't pad; a 25% jump in two months looks like a recording artefact. |
| Access measures tagged "Access measure" / "Contract measure" inconsistently | One assurance vocabulary from the registry: Contract requirement · National ambition · QOF threshold · ICB expectation · Benchmark | Same metric was tagged two ways in v8. |
| Urgent same-day shown against "90%" as if a threshold | "National ambition" chip plus footnote: contract = same-day response; 90% is an ambition | Report §5 rule. |
| QOF and Patient experience each alone in a half-empty 2×2 | One **Quality & income** section with both (name still open) | Three 2×2 sections plus one wide, as specified. |
| Prevention card with red bars and "≈87 missing" | **In development** card, no numbers, lists what it will show | Summed register gaps double-count; the method isn't validated (report §18). |
| PCN rank "4/4 PCN" | "4th of 4 in PCN", dots read left = best | "4/4" read as a score. |
| Attention cards looked like every other card | Attention cards carry a status stripe | Status should read at a glance. |

## L2

- Sections: What is happening → Where → What to look into → **Assessment** (area-level AI text, new) → **Evidence and method** (collapsed) → Explore detailed analysis.
- "Tested / Observed" became **Association / Observed**. "Ruled out" became **No relationship found**.
  Association copy says "tend to", not "get".
- The "callback… contract says" line was reworded to what can be checked; contract claims stay in the registry.

## L3

- Domain **tabs** (e.g. Contact: Day & time · Call outcomes · Trend · PCN · ICB · England), with "← Overview".
- "Funnel" renamed **Call outcomes**, with a note that outcomes overlap and are not additive.

## Data problems found in v8 (now QA items in the payload)

1. **Telephony denominators disagree.** 1,013 calls at 35.8% implies ~2,830 answered; outcomes show 4,570 (86%).
2. **Missed-by-lead-time values** marked as real are identical to the England column in v8's L3 table.
3. **Appointments +25%** since May with nearby practices flat. Rule out a recording change.
4. **Prevention** gaps summed across registers double-count patients.

## Accessibility and hosting

- No values exist only in tooltips: every chart has an `aria-label` summary, and values are printed on the chart or in stats.
- Drawer: focus trap, Esc to close, focus returns to the card; arrow keys move between L3 tabs.
- Light and dark themes from one token set. Only self-contained assets; the web font falls back to the system font.

## Dropped for lack of data

_To be filled in during Step 1 (data inventory)._
Candidates to check: urgent same-day **by weekday** (per practice), telephony **by hour/weekday** (per practice),
GP vs other staff **by booking lead time** (per practice).
