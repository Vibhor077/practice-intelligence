"""
Builds the demo practice payload (Kilburn Park, July 2026) from the v8 prototype content.

This file is a FIXTURE, not the pipeline. It exists so the renderer has a realistic
payload while the real engine (pipeline/) is built. When the engine can emit a payload
for a practice, it must validate against schema/payload.schema.json exactly like this one.

Provenance rules:
  R(...)  -> "real": produced by the July 2026 run
  X(...)  -> "illustrative": placeholder, NEVER shown in demo mode
Values the v8 prototype marked as real are kept as real, even where QA has flagged them
-- the renderer shows real values only, so illustrative ones simply do not appear.
"""
import json, pathlib

def R(d, v=None): return {"d": d, "v": v, "prov": "real"}
def X(d, v=None): return {"d": d, "v": v, "prov": "illustrative"}
def PR(tier, score): return {"tier": tier, "score_internal": score, "reasons": [], "ruleset": "fixture"}

payload = {
  "schema_version": "0.3.0",
  "run": {"id": "demo-2026-07", "generated_at": "2026-09-24T12:00:00Z", "mode": "fixture",
          "versions": {"schema": "0.3.0", "metric_registry": "0.1.0", "ruleset": "0.0.0", "build": "fixture"},
          "source_releases": ["gpad/2026-07", "cbt/2026-07", "ocs/2026-07", "reg/2026-07", "wf/2026-07", "gpps/2026", "qof/2025-26", "imd/2025"]},
  "practice": {
    "ods_code": "E84042", "name": "Kilburn Park Medical Centre",
    "icb": "NHS West and North London ICB", "pcn": {"name": "Kilburn Partnership PCN", "size": 4},
    "period": {"label": "July 2026", "end": "2026-07-31"},
  },
  "context": [
    {"label": "Registered patients", "value": R("6,807", 6807), "delta": X("▲0.4%")},
    {"label": "IMD decile", "value": X("2 / 10", 2), "hint": "1 = most deprived"},
    {"label": "Aged 60+", "value": X("11%", 11)},
    {"label": "Patients per GP", "value": X("2,196", 2196)},
  ],

  # ---------------------------------------------------------------- L1: executive
  "assessment": {
    "lines": [
      {"status": "attention", "area": "contact", "prov": "real",
       "text": "Telephone access is the clearest pressure: over a third of answered calls wait 5+ minutes, three times the ICB rate."},
      {"status": "attention", "area": "qof", "prov": "real",
       "text": "Most unachieved QOF points sit in childhood immunisations, where the new improvement route pays more than the standard thresholds."},
      {"status": "watch", "area": "appointments", "prov": "illustrative",
       "text": "Routine appointment access compares well; urgent same-day should be checked against the 90% national ambition."},
    ],
    "method": "Written from rule-generated findings. Every number is checked against this page's data."
  },
  "attention": {
    "area": "contact", "state": "emerging_pressure",
    "title": "Telephone waiting times",
    "text": "More than a third of answered calls wait over five minutes, the longest in your PCN. Long waits run through the core day, not just the morning peak.",
    "metric": R("35.8%", 35.8), "metric_label": "of answered calls waited 5+ min",
    "compare": [
      {"label": "You", "value": R("35.8%", 35.8), "tone": "crit"},
      {"label": "ICB", "value": R("10.5%", 10.5), "tone": "cmp"},
      {"label": "England", "value": X("12.8%", 12.8), "tone": "cmp"},
    ],
    "scale_max": 50,
    "why": ["Attention status", "4th of 4 in PCN", "3.4× ICB rate", "Patients report the same"],
  },
  "changes": {
    "basis": "July vs May · only 3 months of data so far",
    "items": [
      {"label": "Calls waiting 5+ min", "delta": R("▲ 6.8 pts"), "direction": "up", "good": False,
       "text": "Rising each month since May.", "series": [29, 31, 33, 35.8], "series_prov": "illustrative", "area": "contact"},
      {"label": "Appointments delivered", "delta": R("▲ 25%"), "direction": "up", "good": None,
       "text": "Nearby practices flat.", "series": [100, 111, 125], "series_prov": "real", "area": "workforce",
       "flag": "Verify: possible recording change"},
      {"label": "Urgent seen same day", "delta": X("▼ 5 pts"), "direction": "down", "good": False,
       "text": "Falling as demand rose.", "series": [89, 87, 84], "series_prov": "illustrative", "area": "appointments"},
    ],
  },
  "access_measures": {
    "pending_text": "The four NHS access measures are being calculated from the July 2026 appointments and telephony data.",
    "items": [
      {"label": "Morning calls", "sub": "8–10am, waited 5+ min", "value": {"d": "29.8%", "v": 29.8, "prov": "real", "base": "of 841 answered calls"}, "status": "watch",
       "assurance": "benchmark", "bullet": {"v": 29.8, "max": 60, "cmp_label": "ICB comparison after the national run"}, "area": "contact"},
      {"label": "Core-hours calls", "sub": "10am–6.30pm, waited 5+ min", "value": {"d": "38.2%", "v": 38.2, "prov": "real", "base": "of 1,970 answered calls"}, "status": "attention",
       "assurance": "benchmark", "bullet": {"v": 38.2, "max": 60, "cmp_label": "ICB comparison after the national run"}, "area": "contact"},
      {"label": "Clinically urgent", "sub": "dealt with same day", "value": X("84%", 84), "status": "watch",
       "assurance": "national_ambition", "bullet": {"v": 84, "cmp": 91, "max": 100, "target": 90, "cmp_label": "ICB 91%", "target_label": "Ambition 90%"},
       "footnote": "Contract: urgent requests handled same day. 90% is a national ambition, not a breach line.", "area": "appointments"},
      {"label": "Routine access", "sub": "seen within 7 · 14 days", "value": X("71% · 89%", 89), "status": "good",
       "assurance": "benchmark", "bullet": {"v": 89, "cmp": 81, "max": 100, "cmp_label": "ICB ≤14d 81%"}, "area": "appointments"},
    ],
  },

  # ---------------------------------------------------------------- L1: management areas
  "groups": [
    {"id": "access", "title": "Access", "question": "Can patients reach you, and are they seen in time?"},
    {"id": "capacity", "title": "Capacity & delivery", "question": "Is capacity keeping pace, and where is it being lost?"},
    {"id": "clinical", "title": "QOF & income", "question": "Where is QOF achievement and income opportunity concentrated?"},
    {"id": "quality", "title": "Patient experience", "question": "What are patients telling you, and does it support the operational picture?"},
    {"id": "prevention", "title": "Prevention & population health", "question": "Where might patients be missing preventive or ongoing care?"},
  ],
  "areas": {}
}

A = payload["areas"]

# ---------------------------------------------------------------- Contact & access
A["contact"] = {
  "group": "access", "title": "Patient contact & access", "question": "Can patients reach us when they need us?",
  "status": "attention", "assurance": "benchmark", "priority": PR("high", 0.92),
  "headline": "Patients get through, but a third of answered callers wait too long",
  "metric": {"d": "35.8%", "v": 35.8, "prov": "real", "base": "1,013 of 2,827 answered calls"}, "metric_label": "of answered calls waited 5+ min",
  "card": [{"type": "bullet_rows", "unit": "%", "rows": [
      {"label": "Waited 5+ min", "value": R("35.8%", 35.8), "cmp": 10.5, "max": 50, "tone": "crit"},
      {"label": "Missed calls", "value": R("12.1%", 12.1), "max": 50},
      {"label": "Online requests / 1,000", "value": R("19", 19.4), "cmp": 43, "max": 50, "unit": ""},
  ]}],
  "rank": {"pos": 4, "n": 4}, "trend": {"values": [29, 31, 33, 35.8], "prov": "illustrative"},
  "patient_voice": {"text": X("38% find it easy to phone · ICB 55%"), "verdict": "confirms"},
  "l2": {
    "what": [
      {"value": {"d": "1,013", "v": 1013, "prov": "real", "base": "35.8% of 2,827 answered"}, "label": "calls waited 5+ min", "sub": "ICB [[10.5%]]"},
      {"value": R("780", 779.8), "label": "calls per 1,000 patients", "sub": "5,308 calls · 6,807 patients"},
      {"value": {"d": "12.1%", "v": 12.1, "prov": "real", "base": "640 of 5,308 calls"}, "label": "calls missed", "sub": "includes voicemail"},
      {"value": R("19", 19.4), "label": "online requests per 1,000", "sub": "134 in July · ICB [[43]]"},
    ],
    "where": [
      {"type": "columns", "title": "When calls come in", "note": "Inbound calls in July, by 2-hour block (NHS publishes no finer detail).",
       "unit": "", "prov": "real", "highlight": [1],
       "bars": [{"l": b, "v": v} for b, v in zip(["06–08", "08–10", "10–12", "12–14", "14–16", "16–18", "18–18:30"], [159, 1367, 1072, 985, 909, 674, 73])]},
      {"type": "hbars", "title": "How long answered callers waited, by window", "note": "Share of answered calls that waited more than 5 minutes.", "unit": "%", "max": 50, "prov": "real",
       "rows": [{"l": "8–10am", "v": 29.8, "lab": "29.8% of 841"}, {"l": "10am–6.30pm", "v": 38.2, "tone": "crit", "lab": "38.2% of 1,970"}]},
    ],
    "investigate": [
      {"kind": "observed", "prov": "real", "text": "Most calls arrive 8–10am, but the longest waits are later: 38.2% of callers waited 5+ minutes between 10am and 6.30pm, against 29.8% in the morning peak. Check staffing across the whole core day, not just opening time."},
      {"kind": "observed", "prov": "real", "text": "1 in 5 calls (1,037) ended in the phone menu before reaching the queue. Check what the menu offers; some may be resolved by the recorded message."},
      {"kind": "observed", "prov": "real", "text": "All 804 callbacks requested in July were made."},
      {"kind": "association", "prov": "illustrative", "text": "Practices with high online use tend to receive fewer calls. Yours has low online use and high call volume."},
    ],
    "interpretation": {"prov": "real", "text": "Telephone waiting is the clearest access pressure. Long waits run through the core day rather than only at opening time, and online requests are low. Nothing here shows the cause; staffing across 10am–6.30pm is the place to start."},
    "evidence": {
      "tested_on": "English practices, July 2026",
      "associations": [["Long waits vs ease of phoning (GPPS)", "−0.52"], ["Online use vs call volume", "−0.45"]],
      "no_relationship": [["Reception staff numbers vs phone performance", "−0.001"]],
      "sources": ["Cloud Based Telephony: calls answered metric, durations, day and time (NHS England), Jul 2026", "Online consultation submissions, Jul 2026", "GP Patient Survey 2026", "Patients registered at a GP practice, 1 Aug 2026"],
      "comparators": "Status against ICB. PCN shown as position (4 practices). England in detailed analysis.",
    },
  },
  "l3": {"tabs": [
    {"id": "time", "label": "Day & time", "blocks": [
      {"type": "heatmap", "title": "Average calls per day, by weekday and time", "note": "Inbound calls, July 2026. 2-hour blocks are the finest detail NHS publishes.",
       "prov": "real", "unit": " calls", "cols": ["Mon", "Tue", "Wed", "Thu", "Fri"], "rows": ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00"],
       "max": 80, "values": [[8.5, 9.5, 5.4, 5.8, 6.2], [75.8, 67.2, 51.0, 49.4, 57.2], [60.5, 43.2, 46.2, 42.6, 40.8], [55.2, 40.0, 38.8, 37.4, 42.2], [46.5, 41.0, 38.8, 37.2, 35.0], [37.0, 29.0, 25.8, 27.8, 28.2], [3.8, 3.5, 3.2, 2.8, 2.8]]}]},
    {"id": "outcomes", "label": "Call outcomes", "blocks": [
      {"type": "outcomes", "title": "What happened to calls in July", "note": "These four outcomes add up to all 5,308 calls. Ending in the phone menu is not necessarily a failure.",
       "prov": "real", "steps": [
         {"l": "Calls received", "v": 5308, "p": "100%", "prov": "real"},
         {"l": "Answered by a person", "v": 2827, "p": "53%", "prov": "real"},
         {"l": "Ended in phone menu", "v": 1037, "p": "20%", "prov": "real"},
         {"l": "Asked for a callback", "v": 804, "p": "15%", "prov": "real"},
         {"l": "Missed (incl. voicemail)", "v": 640, "p": "12%", "tone": "crit", "prov": "real"}]}]},
    {"id": "trend", "label": "Trend", "blocks": [
      {"type": "lines", "title": "Long waits and call volume", "note": "Indexed, April = 100. Needs the earlier telephony months.",
       "labels": ["Apr", "May", "Jun", "Jul"], "prov": "illustrative",
       "series": [{"name": "Waited 5+ min", "values": [100, 107, 114, 123], "tone": "crit"},
                  {"name": "Calls / 1,000", "values": [100, 102, 105, 109], "tone": "practice"}]}]},
    {"id": "compare", "label": "PCN · ICB · England", "blocks": [
      {"type": "table", "title": "Compared with peers", "columns": ["Measure", "You", "PCN position", "ICB", "England"],
       "rows": [["Waited 5+ min", R("35.8%"), X("4 of 4"), X("10.5%"), X("12.8%")],
                ["Calls per 1,000", R("780"), X("4 of 4"), X("610"), X("598")],
                ["Missed calls", R("12.1%"), X("–"), X("–"), X("–")]]}]},
  ]},
}

# ---------------------------------------------------------------- Appointment access
A["appointments"] = {
  "group": "access", "title": "Appointment access", "question": "Are patients getting appropriate care quickly enough?",
  "status": "watch", "assurance": "national_ambition", "priority": PR("medium", 0.55),
  "headline": "Routine waits compare well; urgent same-day is below the 90% ambition",
  "metric": X("84%", 84), "metric_label": "of clinically urgent requests dealt with same day",
  "card": [{"type": "bullet_rows", "unit": "%", "rows": [
      {"label": "Urgent same day", "value": X("84%", 84), "cmp": 91, "target": 90, "max": 100, "tone": "warn"},
      {"label": "Routine ≤ 14 days", "value": X("89%", 89), "cmp": 81, "max": 100, "tone": "good"},
  ]}],
  "rank": {"pos": 2, "n": 4}, "trend": {"values": [89, 87, 84], "prov": "illustrative"},
  "patient_voice": {"text": X("81% happy with time offered · ICB 77%"), "verdict": "consistent"},
  "l2": {
    "what": [
      {"value": X("84%"), "label": "urgent dealt with same day", "sub": "National ambition 90%"},
      {"value": X("89%"), "label": "routine within 14 days", "sub": "ICB 81%"},
      {"value": X("21%"), "label": "requests coded urgent", "sub": "ICB 23%"},
    ],
    "where": [
      {"type": "hbars", "title": "Median wait for a routine appointment", "note": "Grey tick = ICB.", "unit": " days", "max": 12, "prov": "illustrative",
       "rows": [{"l": "GP", "v": 9, "c": 7}, {"l": "Nurse / other staff", "v": 4, "c": 5}]},
    ],
    "investigate": [
      {"kind": "observed", "prov": "illustrative", "text": "Urgent same-day fell while total appointments rose. Check whether urgent capacity grew with demand."},
      {"kind": "observed", "prov": "illustrative", "text": "GP routine waits are longer than the ICB; other staff are faster. The gap is GP-specific."},
    ],
    "interpretation": {"prov": "illustrative", "text": "Routine access is a relative strength. The urgent same-day rate is the measure to confirm first, because it sits against a national ambition."},
    "evidence": {"tested_on": "6,076 English practices, July 2026",
      "associations": [["Urgent coding share vs ICB", "Within range"]], "no_relationship": [["Booking wait vs survey wait complaint", "+0.16"]],
      "sources": ["Appointments in General Practice (GPAD), Jul 2026", "2026/27 GP contract access requirements"],
      "comparators": "Status against the national ambition where one exists, otherwise ICB."},
  },
  "l3": {"tabs": [
    {"id": "delivery", "label": "Delivery", "blocks": [
      {"type": "hbars", "title": "How appointments were delivered", "note": "Grey tick = ICB.", "unit": "%", "max": 80, "prov": "illustrative",
       "rows": [{"l": "Face to face", "v": 61, "c": 66}, {"l": "Telephone", "v": 34, "c": 29}, {"l": "Video / online", "v": 3, "c": 3}, {"l": "Home visit", "v": 2, "c": 2}]}]},
    {"id": "staff", "label": "Staff & lead time", "blocks": [
      {"type": "table", "title": "Appointments by staff type and time from booking", "note": "Shown only if national data gives this breakdown per practice. To confirm.",
       "columns": ["Booked", "GP", "Other staff"],
       "rows": [[r[0], X(r[1]), X(r[2])] for r in [["Same day", "1,120", "840"], ["Next day", "310", "260"], ["2–7 days", "520", "480"], ["8–28 days", "690", "510"], ["28+ days", "140", "230"]]]}]},
  ]},
}

# ---------------------------------------------------------------- Workforce & capacity
A["workforce"] = {
  "group": "capacity", "title": "Workforce & capacity", "question": "Is our capacity keeping pace with population and workload?",
  "status": "watch", "assurance": "benchmark", "priority": PR("medium", 0.5),
  "headline": "Appointment activity is rising faster than GP capacity",
  "metric": X("2,196", 2196), "metric_label": "patients per GP FTE · ICB 1,980",
  "card": [{"type": "lines", "labels": ["May", "Jun", "Jul"], "prov": "mixed", "compact": True, "note": "Indexed, May = 100",
            "series": [{"name": "Appointments", "values": [100, 111, 125], "tone": "practice", "prov": "real"},
                       {"name": "GP FTE", "values": [100, 100, 99], "tone": "accent", "prov": "illustrative"},
                       {"name": "Patients", "values": [100, 100.2, 100.4], "tone": "cmp", "prov": "illustrative"}]}],
  "rank": {"pos": 3, "n": 4},
  "l2": {
    "what": [
      {"value": X("2,196"), "label": "patients per GP FTE", "sub": "ICB 1,980"},
      {"value": X("3.1"), "label": "GP FTE", "sub": "Excluding trainees"},
      {"value": R("▲ 25%"), "label": "appointments since May", "sub": "GP FTE broadly flat"},
      {"value": R("6,807"), "label": "registered patients", "sub": "▲0.4% on June"},
    ],
    "where": [
      {"type": "hbars", "title": "Current workforce", "note": "FTE. Grey tick = ICB practice of the same list size.", "unit": "", "max": 7, "prov": "illustrative",
       "rows": [{"l": "GP", "v": 3.1, "c": 3.4}, {"l": "Nurse", "v": 2.4, "c": 2.2}, {"l": "Admin", "v": 6.2, "c": 5.8}]},
    ],
    "investigate": [
      {"kind": "observed", "prov": "real", "text": "Appointments rose 25% in two months. Check first whether this is a real change or a change in how appointments are recorded."},
      {"kind": "observed", "prov": "illustrative", "text": "If real, check which staff groups and appointment modes absorbed the increase."},
      {"kind": "observed", "prov": "illustrative", "text": "List growth is small month to month; assess it over 6–12 months alongside workforce."},
    ],
    "interpretation": {"prov": "illustrative", "text": "Activity is outpacing GP capacity on paper, but the size of the jump needs verifying before it is treated as a pressure."},
    "evidence": {"tested_on": "6,076 English practices, July 2026",
      "associations": [], "no_relationship": [["Staffing level vs access performance", "Not established"]],
      "sources": ["General Practice Workforce (NHS Digital)", "Patients registered at a GP practice", "GPAD, May–Jul 2026"],
      "comparators": "ICB. Workforce denominator (GP FTE definition) still to be confirmed."},
  },
  "l3": {"tabs": [
    {"id": "trend", "label": "Trends", "blocks": [
      {"type": "lines", "title": "Six-month workforce, population and activity", "note": "Indexed, February = 100.", "labels": ["Feb", "Mar", "Apr", "May", "Jun", "Jul"], "prov": "mixed",
       "series": [{"name": "Appointments", "values": [100, 103, 107, 111, 118, 125], "tone": "practice", "prov": "real"},
                  {"name": "Patients", "values": [100, 100.2, 100.4, 100.5, 100.8, 101.0], "tone": "cmp", "prov": "illustrative"},
                  {"name": "GP FTE", "values": [100, 100, 99.8, 100, 99.5, 99], "tone": "accent", "prov": "illustrative"}]}]},
    {"id": "compare", "label": "Comparators", "blocks": [
      {"type": "table", "title": "Capacity compared", "columns": ["Measure", "You", "PCN", "ICB", "England"],
       "rows": [["Patients per GP FTE", X("2,196"), X("2,040"), X("1,980"), X("1,930")], ["Appointments per 1,000", X("512"), X("458"), X("430"), X("445")]]}]},
  ]},
}

# ---------------------------------------------------------------- Missed appointments
A["missed"] = {
  "group": "capacity", "title": "Missed appointments", "question": "Where are we losing usable appointment capacity?",
  "status": "watch", "assurance": "benchmark", "priority": PR("medium", 0.45),
  "headline": "Missed appointments cluster in bookings made further ahead",
  "metric": R("7.5%", 7.5), "metric_label": "of appointments missed in July · 9.4% in May",
  "card": [{"type": "columns", "unit": "%", "prov": "real", "compact": True, "title": "Missed, by time from booking",
            "bars": [{"l": "Same day", "v": 1.8}, {"l": "Next day", "v": 3.9}, {"l": "2–7 d", "v": 6.1}, {"l": "8–28 d", "v": 7.4}, {"l": "28+ d", "v": 8.9}]}],
  "rank": {"pos": 3, "n": 4}, "trend": {"values": [9.4, 7.6, 7.5], "prov": "real"},
  "l2": {
    "what": [
      {"value": R("7.5%"), "label": "missed in July", "sub": "9.4% in May"},
      {"value": R("240"), "label": "missed appointments", "sub": "July"},
      {"value": R("8.9%"), "label": "missed when booked 28+ days ahead", "sub": "Highest band"},
    ],
    "where": [
      {"type": "columns", "title": "Missed, by time from booking", "unit": "%", "prov": "real",
       "bars": [{"l": "Same day", "v": 1.8}, {"l": "Next day", "v": 3.9}, {"l": "2–7 days", "v": 6.1}, {"l": "8–28 days", "v": 7.4}, {"l": "28+ days", "v": 8.9}]},
    ],
    "investigate": [
      {"kind": "observed", "prov": "real", "text": "The further ahead an appointment is booked, the more often it is missed. Check reminders and confirmation for bookings 8+ days out."},
      {"kind": "observed", "prov": "real", "text": "The rate has improved since May. Keep what changed while investigating the rest."},
    ],
    "interpretation": {"prov": "real", "text": "Missed appointments are improving, and the remaining loss is concentrated in long-lead bookings, which is where reminders act."},
    "evidence": {"tested_on": "6,076 English practices, July 2026",
      "associations": [["Booking distance vs missed rate", "1.8% → 8.9%"]], "no_relationship": [["Access measures vs missed rate", "No clear relationship"]],
      "sources": ["GPAD appointment status by time between booking and appointment, Jul 2026"],
      "comparators": "ICB and own trend."},
  },
  "l3": {"tabs": [
    {"id": "trend", "label": "Trend", "blocks": [
      {"type": "lines", "title": "Missed rate", "note": "% of appointments.", "labels": ["May", "Jun", "Jul"], "prov": "mixed", "absolute": True, "unit": "%",
       "series": [{"name": "You", "values": [9.4, 7.6, 7.5], "tone": "practice", "prov": "real"}, {"name": "ICB", "values": [7.1, 7.0, 6.9], "tone": "cmp", "prov": "illustrative"}]}]},
    {"id": "lead", "label": "Lead time", "blocks": [
      {"type": "hbars", "title": "Missed by time from booking", "note": "Grey tick = ICB.", "unit": "%", "max": 10, "prov": "mixed",
       "rows": [{"l": "Same day", "v": 1.8, "c": 1.7}, {"l": "Next day", "v": 3.9, "c": 3.5}, {"l": "2–7 days", "v": 6.1, "c": 5.6}, {"l": "8–28 days", "v": 7.4, "c": 6.8}, {"l": "28+ days", "v": 8.9, "c": 8.0}], "cmp_prov": "illustrative"}]},
  ]},
}

# ---------------------------------------------------------------- QOF
A["qof"] = {
  "group": "clinical", "title": "QOF & income opportunity", "question": "Where are we leaving QOF achievement and income on the table?",
  "status": "attention", "assurance": "qof_threshold", "priority": PR("high", 0.7),
  "headline": "Most unachieved QOF points are in childhood immunisations",
  "metric": R("75.2", 75.2), "metric_label": "QOF points not achieved · 86.7% achieved (2025/26)",
  "card": [{"type": "bullet_rows", "unit": " pts", "rows": [
      {"label": "Childhood imms", "value": R("54 pts", 54), "max": 60, "tone": "crit"},
      {"label": "Cervical screening", "value": X("9.1 pts", 9.1), "max": 60},
      {"label": "Blood pressure", "value": X("6.4 pts", 6.4), "max": 60},
  ]}],
  "rank": {"pos": 3, "n": 4}, "trend": {"values": [88.9, 87.4, 86.7], "prov": "illustrative"},
  "l2": {
    "what": [
      {"value": R("86.7%"), "label": "points achieved", "sub": "Similar practices [[91%]]"},
      {"value": R("75.2"), "label": "points not achieved", "sub": "54 in immunisations"},
      {"value": X("▼ 2.2"), "label": "points vs last year", "sub": "Like-for-like indicators"},
    ],
    "where": [
      {"type": "hbars", "title": "Distance to the upper threshold", "note": "Black line = QOF upper threshold. Points at stake on the right.", "unit": "%", "max": 100, "prov": "illustrative",
       "rows": [{"l": "MMR at 2 years", "v": 71, "t": 95, "lab": "71% · 18 pts"}, {"l": "MMR at 5 years", "v": 69, "t": 95, "lab": "69% · 18 pts"},
                {"l": "8 weeks – 1 year", "v": 78, "t": 95, "lab": "78% · 18 pts"}, {"l": "Cervical 25–49", "v": 62, "t": 80, "lab": "62% · 5.8 pts"}]},
    ],
    "investigate": [
      {"kind": "observed", "prov": "real", "text": "Childhood immunisations account for 54 of the 75 points not achieved."},
      {"kind": "observed", "prov": "illustrative", "text": "In 2026/27 the improvement route pays [[31 of 54]] points here against [[14]] on the standard thresholds."},
      {"kind": "observed", "prov": "real", "text": "For each gap, check 'not done' against 'exception reported'. They need different fixes."},
      {"kind": "association", "prov": "real", "text": "Deprivation and age both move QOF scores, so the comparison is with similar practices, not the ICB average."},
    ],
    "interpretation": {"prov": "real", "text": "QOF opportunity is concentrated rather than spread: one domain holds most of the missing points, which makes it a focused piece of work."},
    "evidence": {"tested_on": "6,076 English practices, 2025/26",
      "associations": [["Deprivation vs QOF achievement", "−0.29"], ["Older population vs QOF achievement", "+0.29"]], "no_relationship": [["Call handling vs QOF", "−0.08"]],
      "sources": ["QOF 2025/26 achievement (NHS Digital)", "QOF 2026/27 guidance"],
      "comparators": "Similar practices (peer group definition to be finalised). Annual data: describes the closed year."},
  },
  "l3": {"tabs": [
    {"id": "indicators", "label": "Indicators", "blocks": [
      {"type": "table", "title": "Indicators with the most points to recover", "note": "Immunisation total (54 pts) is real; the split by indicator is a placeholder.",
       "columns": ["Indicator", "Achieved", "Upper threshold", "Exceptions", "Points lost", "England"],
       "rows": [["MMR at 2 (VI002)", X("71%"), R("95%"), X("1%"), X("18.0"), X("88%")],
                ["MMR at 5 (VI003)", X("69%"), R("95%"), X("1%"), X("18.0"), X("85%")],
                ["8 wks–1 yr (VI001)", X("78%"), R("95%"), X("2%"), X("18.0"), X("91%")],
                ["Cervical 25–49", X("62%"), R("80%"), X("4%"), X("5.8"), X("72%")]]}]},
    {"id": "route", "label": "Improvement route", "blocks": [
      {"type": "hbars", "title": "Immunisations: two ways to earn points in 2026/27", "unit": " pts", "max": 54, "prov": "illustrative",
       "rows": [{"l": "Standard thresholds", "v": 14, "lab": "14 of 54 pts"}, {"l": "Improve on own 2-yr baseline", "v": 31, "tone": "good", "lab": "31 of 54 pts"}]}]},
  ]},
}

# ---------------------------------------------------------------- Patient experience
A["experience"] = {
  "group": "quality", "title": "Patient experience", "question": "What are patients telling us, and does it match the operational evidence?",
  "status": "watch", "assurance": "benchmark", "priority": PR("low", 0.4),
  "headline": "Patients confirm the phone problem; appointment times are rated well",
  "metric": X("38%", 38), "metric_label": "find it easy to contact the practice by phone",
  "card": [{"type": "bullet_rows", "unit": "%", "rows": [
      {"label": "Easy to phone", "value": X("38%", 38), "cmp": 55, "max": 100, "tone": "crit"},
      {"label": "Happy with time", "value": X("81%", 81), "cmp": 77, "max": 100, "tone": "good"},
      {"label": "Good overall", "value": X("72%", 72), "cmp": 76, "max": 100},
  ]}],
  "rank": {"pos": 3, "n": 4},
  "l2": {
    "what": [
      {"value": X("38%"), "label": "find it easy to phone", "sub": "ICB 55%"},
      {"value": X("81%"), "label": "happy with appointment time", "sub": "ICB 77%"},
      {"value": X("72%"), "label": "good overall experience", "sub": "ICB 76%"},
    ],
    "where": [
      {"type": "paired", "title": "What patients say against what the data shows", "prov": "illustrative",
       "rows": [{"patient": "38% find it easy to phone", "operational": "35.8% of answered calls wait 5+ min", "verdict": "confirms", "area": "contact"},
                {"patient": "81% happy with appointment time", "operational": "89% of routine seen within 14 days", "verdict": "consistent", "area": "appointments"}]},
    ],
    "investigate": [
      {"kind": "observed", "prov": "illustrative", "text": "Patient feedback supports the telephone finding rather than contradicting it."},
      {"kind": "observed", "prov": "illustrative", "text": "Satisfaction with appointment times is strong despite the urgent same-day signal."},
    ],
    "interpretation": {"prov": "illustrative", "text": "Patients and the operational data tell the same story about the phones, which makes that finding stronger."},
    "evidence": {"tested_on": "6,076 English practices, GPPS 2026",
      "associations": [["Long waits vs ease of phoning", "−0.52"]], "no_relationship": [["Routine wait vs time satisfaction", "No clear contradiction"]],
      "sources": ["GP Patient Survey 2026 (fieldwork Jan–Mar)"],
      "comparators": "ICB. Survey is annual, so it lags the operational data."},
  },
  "l3": {"tabs": [
    {"id": "dims", "label": "Dimensions", "blocks": [
      {"type": "hbars", "title": "Patient experience", "note": "Grey tick = ICB.", "unit": "%", "max": 100, "prov": "illustrative",
       "rows": [{"l": "Easy to phone", "v": 38, "c": 55, "tone": "crit"}, {"l": "Helpful reception", "v": 79, "c": 81}, {"l": "Choice of time", "v": 71, "c": 69}, {"l": "Satisfied with time", "v": 81, "c": 77}, {"l": "Overall experience", "v": 72, "c": 76}]}]},
  ]},
}

# ---------------------------------------------------------------- Prevention (in development)
A["prevention"] = {
  "group": "prevention", "title": "Prevention & population health", "question": "Where might preventive or ongoing care need further investigation?",
  "availability": "not_built", "status": "watch", "assurance": "none", "priority": PR("low", 0.3), "wide": True,
  "headline": "Recorded disease prevalence compared with similar areas",
  "metric": X("3 of 8", 3), "metric_label": "registers below the ICB rate · recorded prevalence, not modelled",
  "card": [{"type": "bullet_rows", "unit": "%", "prov": "illustrative", "rows": [
      {"label": "Hypertension", "value": X("9.0%", 9.0), "cmp": 11.2, "max": 20},
      {"label": "Diabetes", "value": X("6.4%", 6.4), "cmp": 7.1, "max": 20},
      {"label": "Atrial fibrillation", "value": X("0.8%", 0.8), "cmp": 1.2, "max": 20}]}],
  "l2": {
    "what": [{"value": X("9.0%"), "label": "hypertension recorded prevalence", "sub": "ICB 11.2%"}],
    "where": [], "investigate": [], "interpretation": {"prov": "illustrative", "text": ""},
    "evidence": {"tested_on": "", "associations": [], "no_relationship": [], "sources": ["QOF registers 2025/26", "Patients registered by age"], "comparators": "PCN and ICB recorded prevalence. Age-standardisation to be decided."}},
}

payload["footer"] = {
  "sources": "NHS England GP appointments data, cloud-based telephony, online consultation submissions, GP workforce, patient registrations, QOF, GP Patient Survey, English indices of deprivation.",
  "licence": "Contains public sector information licensed under the Open Government Licence v3.0.",
  "note": "L1 prioritises. L2 explains. L3 provides detailed analysis. Status is set against the ICB unless a national ambition or QOF threshold applies. PCN is shown as a rank. Links between measures are patterns across practices, not proof of cause.",
}

out = pathlib.Path(__file__).with_name("demo-kilburn-park.json")
out.write_text(json.dumps(payload, indent=1, ensure_ascii=False))
print("wrote", out)
