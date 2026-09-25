# Patient Contact & Access: source map

**Status:** draft for review (25 Sep 2026). This is the specification for the first vertical slice.
**Management question:** Can patients reach us when they need us?
**Verified against:** July 2026 raw files in `pi-data/raw/`. The worked example is Kilburn Park Medical Centre, **E84042**.

A number goes on the page only when this map says *Supported* or *Derivable*, the registry entry exists, and the Kilburn Park check below passes.

---

## 1. Sources used

| Code | Dataset (NHS England) | File(s) in `raw/` | Grain | Period in hand |
|---|---|---|---|---|
| `cbt_ans` | Cloud Based Telephony: Calls Answered Metric | `cbt/2026-07/…Calls Answered Metric…zip` (one CSV per region, `_Y56` etc.) | practice × day × wait band × core window | Jul 2026 |
| `cbt_dur` | Cloud Based Telephony: By Durations | `cbt/2026-07/…By Durations…zip` | practice × day × indicator × band | Jul 2026 |
| `cbt_dt` | Cloud Based Telephony: By Day and Time | `cbt/2026-07/…By Day and Time…zip` | practice × day × indicator × 2-hour band | Jul 2026 |
| `cbt_part` | CBT participation and submission breakdown | `cbt/2026-07/CBT-participation…xlsx`, sheet `Table 1`, header row 15 | practice | Jul 2026 |
| `ocs` | Submissions via Online Consultation Systems | `ocs/2026-07/…in General Practice…zip` (north / south CSVs) | practice × month × metric | **Feb 2025 – Jul 2026** |
| `ocs_dt` | OC submissions by day and time | `ocs/2026-07/…By Day and Time…zip` | practice × day × hour | Jul 2026 |
| `gpps` | GP Patient Survey 2026 | `gpps/2026/GPPS_2026_Practice_data_(weighted)_(csv)_PUBLIC.csv` | practice | 2026 survey |
| `reg` | Patients registered at a GP practice | `reg/2026-07/gp-reg-pat-prac-all.zip` | practice | list at **1 Aug 2026** |
| `map` | Practice → PCN → ICB mapping | `gpad/2026-07/Practice_Level_Crosstab_Jul_26.zip` → `Mapping.csv` | practice | Jul 2026 |

Definitions come from NHS England's CBT support information page and the metadata workbooks in `cbt/_metadata/` and `ocs/_metadata/`.

## 2. Telephony indicator codes

| Code | NHS definition | Breakdown |
|---|---|---|
| CBT001 | Inbound calls | TOTAL; 2-hour time band |
| CBT002 | Calls ended in the phone menu (IVR), before the queue | TOTAL |
| CBT003 | Answered by a person, by wait time | wait bands `0`, `1_30` … `241_300`, `>300` seconds; core window |
| CBT004 | Missed: the caller expected a person and wasn't answered, including voicemail | wait-before-ending bands |
| CBT005 | Callback requested while queuing (virtual queue) | TOTAL |
| CBT006 | Callback made | TOTAL |
| CBT007 | Answered calls by call length | should equal CBT003 in total |

Core windows (`cbt_ans`): `Core_8_10` = 8–10am, `Core_10_1830` = 10am–6.30pm, `Non-Core`.
Time bands (`cbt_dt`): 00:00-05:59, 06:00-07:59, 08:00-09:59, 10:00-11:59, 12:00-13:59, 14:00-15:59, 16:00-17:59, 18:00-18:29, 18:30-23:59.

## 3. When a practice's telephony is available

From `cbt_part` (July 2026, 6,180 practices):

| Participates | Included in publication | Shared supplier account | Practices | Availability |
|---|---|---|---|---|
| Yes | Yes | No | 4,972 | `available` |
| Yes | Yes | **Yes** | 347 | `no_data`: "Telephony data is shared with other practices on the same phone account and can't be shown for this practice alone." |
| Yes | No | No | 797 | `no_data`: "Telephony data was not published for this practice this month." |
| No | No | No | 64 | `no_data`: "This practice does not take part in the NHS telephony data collection." |

Attribution rule: **shared-account data must never be assigned to one practice.** This is an `attribution_level` constraint in the registry.

Practices with no telephony still show online consultation and patient survey findings in L2. But the Contact & Access **headline** is telephony-led, so the card goes inactive.

## 4. Element-by-element map

Verdicts: **Supported** = read or computed directly · **Derivable** = needs other practices or earlier months · **Unsupported** = the data can't give it (drop or reword).

### L1 card

| Element | Metric / source | Calculation | Verdict |
|---|---|---|---|
| Headline metric: "% of answered calls that waited 5+ min" | `tel_wait_5m_pct` · `cbt_ans` | Σ CBT003 `>300` ÷ Σ CBT003 (all bands, all windows), month | Supported |
| Bullet row "Waited 5+ min" + ICB tick | as above + ICB median | median over available practices in the same ICB | Derivable (all-practice run) |
| Bullet row "Missed calls" (v8 "Not answered") | `tel_missed_pct` · `cbt_dur` | Σ CBT004 ÷ Σ CBT001 | Supported |
| Bullet row "Online requests / 1,000" | `ocs_per_1000` · `ocs` | `OC_RATE_PER_1000_REGISTERED_PATIENTS` as published | Supported |
| Patient voice "x% find it easy to phone · ICB y%" | `gpps_phone_ease` · `gpps` | `localgpservicesphone.pcteval` (excludes "haven't tried"); CI `lowileval`/`hiwileval` | Supported (ICB comparison: Derivable) |
| Patient voice verdict (confirms / consistent / contradicts / unavailable) | rule | operational status vs GPPS position, **CI-aware** | Derivable (rule to define) |
| PCN rank "4 of 4 practices" | from `map` + all-practice metric | rank within PCN; direction from the registry; omit if ties, n < 3 or coverage differs | Derivable |
| Trend sparkline | `tel_wait_5m_pct` over months | needs ≥ 3 months | **Blocked** until older CBT months are downloaded |
| Status pill | rule | ICB-relative rule (thresholds to calibrate) | Derivable |

### Access-measure strip (the two call-wait cards)

| Element | Calculation | Verdict |
|---|---|---|
| "Morning calls, 8–10am: % waited 5+ min" | CBT003 `>300` ÷ CBT003, `Core_8_10` | Supported |
| "Core hours, 10am–6.30pm: % waited 5+ min" | same, `Core_10_1830` | Supported |
| v8 "Morning call wait **6m 40s**" (average time) | an average can't be computed from bands with an open top band (`>300`) | **Unsupported**: reword to a share |

Assurance for both: `benchmark`. **Verify** whether the 2026/27 contract sets a telephony standard before using any other label.

### L2 drawer: What is happening

| Stat | Calculation | Verdict |
|---|---|---|
| Calls waited 5+ min (count) | Σ CBT003 `>300` | Supported |
| Calls per 1,000 patients | Σ CBT001 ÷ `reg` list × 1,000 | Supported |
| Missed calls % | Σ CBT004 ÷ Σ CBT001 | Supported |
| Online requests per 1,000 | as published | Supported |

### L2: Where it is happening

| Visual | Calculation | Verdict |
|---|---|---|
| Calls by time of day (bars) | Σ CBT001 per 2-hour band, month | Supported, **2-hour bands, not hourly** |
| Long waits by time of day | the long-wait share is only published by core window (8–10 / 10–18:30 / non-core), **not** by 2-hour band | **Reword**: show volume by band, plus long-wait share by the 3 windows |
| Online requests by weekday × hour | `ocs_dt` TOTAL; clinical vs admin | Supported |

### L2: What to look into (examples; the rules decide which appear)

| Item | Kind | Basis | Verdict |
|---|---|---|---|
| Long waits concentrated in a window | Observed | window shares (Kilburn: 38.2% core vs 29.8% morning) | Supported |
| Callbacks requested but not made | Observed | CBT005 − CBT006 | Supported |
| Share of calls ending in the phone menu | Observed | CBT002 ÷ CBT001, **worded neutrally** (may be resolved by a recorded message) | Supported |
| Low online use alongside high call volume | Tested | cross-practice association | Derivable: needs the evidence rule |
| Long waits ↔ GPPS phone ease | Tested | cross-practice association | Derivable: needs the evidence rule |

### L3 tabs

| Tab | Content | Verdict |
|---|---|---|
| Day & time | calls by weekday × 2-hour band (heatmap of **volume**) | Supported |
| Call outcomes | IVR-ended / answered / missed / callback requested, share of inbound, plus reconciliation to CBT001 | Supported |
| Trend | monthly long-wait %, calls / 1,000, online / 1,000 | Online: Supported (18 months) · Telephony: **Blocked** (history) |
| PCN · ICB · England | table of the practice vs PCN rank vs ICB median vs England median | Derivable |

### Evidence tab

Sources and comparators only, until the evidence rule exists (minimum N, method, missing-value treatment, effect-size threshold). No r values are shown before then.

## 5. Kilburn Park E84042, July 2026: expected values (test fixture)

Hand-calculated from raw files on 25 Sep 2026. The pipeline must reproduce these exactly.

| Measure | Value |
|---|---|
| Registered patients (`reg`, 1 Aug 2026) | 6,807 |
| Inbound calls CBT001 | 5,308 |
| Calls per 1,000 | 779.8 |
| Ended in IVR CBT002 | 1,037 (19.5%) |
| Answered CBT003 | 2,827 (53.3%) |
| Missed CBT004 | 640 (12.1%) |
| Callbacks requested / made CBT005 / CBT006 | 804 / 804 |
| **Outcomes reconcile** 1,037 + 2,827 + 640 + 804 | **5,308 = CBT001 ✓** |
| Answered by length CBT007 | 2,827 = CBT003 ✓ |
| Answered, waited >5 min | 1,013 → **35.8%** |
| 8–10am: answered / >5 min | 841 / 251 → 29.8% |
| 10am–6.30pm: answered / >5 min | 1,970 / 753 → 38.2% |
| Non-core: answered / >5 min | 16 / 9 |
| Busiest band (calls) | 08:00–09:59: 1,367 |
| Online requests | 134 (98 clinical, 36 admin); 19.4 per 1,000 (NHS denominator 6,920) |
| Telephony availability | Participates · Included · Not shared → `available` |
| PCN | Kilburn Partnership PCN (U25131), 4 practices |
| ICB | NHS West and North London ICB (Z9B2Z) |

## 6. Data-handling rules found during the inventory

1. **Read CSVs with a real CSV parser.** OCS files contain quoted names with commas, so naive splitting breaks.
2. **Region-split files:** CBT has one file per region (`_Y56` … `_Y63`, plus `_Unmapped`); OCS has north and south files. Load all of them. **Unmapped** rows are excluded and counted in the run report.
3. **Two list-size denominators exist.** Our calls per 1,000 uses `reg` (6,807); NHS's OC rate uses its own `PATIENTS_REGISTERED` (6,920). Show the published OC rate as it stands, and record the denominator in provenance. Never mix the two in one ratio.
4. **Registration dating:** `reg/2026-07/` holds the list at 1 Aug 2026. Record the extract date as the metric's `as_of`.
5. **Reconciliation check per practice:** CBT002 + CBT003 + CBT004 + CBT005 should equal CBT001, and CBT007 should equal CBT003. On a mismatch, show the data but add a practice-level data-quality flag. NHS warns that many practices don't reconcile.
6. **Missing ≠ zero:** a practice with no CBT rows has no telephony data. It does not have 0 calls.
7. **Mapping is effective-dated:** use the `map` for the same period. London now has four ICBs; v8's "North West London" name is out of date.

## 7. Blocked or open

| Item | Blocker | Action |
|---|---|---|
| Telephony trend, What Changed (telephony) | only July in hand | download earlier CBT months |
| Status thresholds, priority, PCN tie rule | need all-practice distributions | calibrate after the first national run |
| Patient-voice verdict rule | define using GPPS confidence intervals | draft with the rules engine |
| Evidence ("Tested") items | evidence rule not defined | leave out until defined |
| Telephony access-measure assurance | does the 2026/27 contract set a telephony standard? | verify in the contract documents |
| England comparator | cheap to compute; **L3 only** | presentation rule |

## 8. Registry changes this map implies

- `tel_answered_pct` → denominator CBT001; `tel_wait_5m_pct` → denominator **CBT003 (answered)**
- add `tel_ivr_ended_pct`, `tel_missed_pct`, `tel_callback_gap`, `tel_wait_5m_pct_core_8_10`, `tel_wait_5m_pct_core_10_1830`, `tel_calls_by_band`
- remove `tel_wait_mean_morning` / `tel_wait_mean_core` (unsupported), and `tel_wait_5m_by_hour` (not published at that grain)
- add `attribution_level: practice` with the shared-account exclusion on every telephony metric
- `ocs_per_1000`: source field `OC_RATE_PER_1000_REGISTERED_PATIENTS`, denominator noted as NHS's own
- `gpps_phone_ease`: `localgpservicesphone.pcteval` with CI fields
