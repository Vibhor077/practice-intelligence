"""
Semantic checks the JSON schema cannot express. These encode product rules, so a payload
that passes the schema can still be refused here. Run in CI on every generated payload.

  python tools/lint_payload.py payloads/*.json          # exit 1 on any ERROR
"""
import json, sys, pathlib

def lint(p):
    E, W = [], []
    areas = p["areas"]
    fixture = p["run"]["mode"] == "fixture"
    av = lambda a: a.get("availability", "available")
    score = lambda a: (a.get("priority") or {}).get("score_internal", 0)
    live = {k: a for k, a in areas.items() if av(a) == "available"}

    # 1. Every area reference resolves
    refs = [("assessment", l["area"]) for l in p["assessment"]["lines"]] + [("attention", p["attention"]["area"])] \
         + [("changes", c["area"]) for c in p["changes"]["items"]] + [("access_measures", m["area"]) for m in p["access_measures"]["items"]]
    for where, r in refs:
        if r not in areas: E.append(f"{where}: unknown area '{r}'")
    for k, a in areas.items():
        if a["group"] not in {g["id"] for g in p["groups"]}: E.append(f"area {k}: unknown group '{a['group']}'")

    # 2. The attention panel points at the highest-priority live area (v8 bug: it did not)
    top = max(live, key=lambda k: score(live[k]))
    if p["attention"]["area"] != top:
        E.append(f"attention: points at '{p['attention']['area']}' but highest priority is '{top}'")
    if p["attention"]["metric"]["prov"] != "real":
        E.append("attention: headline metric must be real data")
    if areas.get(p["attention"]["area"]) and av(areas[p["attention"]["area"]]) != "available":
        E.append("attention: points at an area that is not available")

    # 3. Assessment line status agrees with the area it names (v8 bug: QOF 'attention' shown as ✓)
    for l in p["assessment"]["lines"]:
        a = areas.get(l["area"])
        if a and l["status"] != a["status"]:
            E.append(f"assessment: line for '{l['area']}' is '{l['status']}' but area is '{a['status']}'")

    # 4. Assurance language: contract_attention only for contract requirements
    if p["attention"]["state"] == "contract_attention" and areas[p["attention"]["area"]]["assurance"] != "contract_requirement":
        E.append("attention: 'contract_attention' used for a measure that is not a contract requirement")

    # 5. Status ordering vs priority: an 'attention' area should outrank any 'watch' area
    rank = {"attention": 3, "watch": 2, "normal": 1, "good": 1, "unable": 0}
    for k, a in live.items():
        for k2, b in live.items():
            if rank.get(a["status"], 0) > rank.get(b["status"], 0) and score(a) < score(b):
                W.append(f"priority: '{k}' ({a['status']}) scores below '{k2}' ({b['status']})")

    # 6. Availability: unsupported areas carry no figures; in pipeline mode, not_built areas carry none either
    for k, a in areas.items():
        figs = any(x in a for x in ("metric", "card", "l2", "l3"))
        if av(a) == "unsupported" and figs:
            E.append(f"area {k}: unsupported but carries figures")
        if av(a) == "not_built" and figs and not fixture:
            E.append(f"area {k}: not_built but carries figures in a pipeline payload")
        if av(a) == "no_data" and not a.get("unavailable_reason"):
            E.append(f"area {k}: no_data without a reason for the practice")

    # 7. Changes are not padded: each must have >= 3 points to show a pattern
    for c in p["changes"]["items"]:
        if len(c["series"]) < 3: W.append(f"changes: '{c['label']}' has fewer than 3 points")

    # 8. Provenance: pipeline payloads may contain real data only
    ill = json.dumps(p).count('"prov": "illustrative"')
    if ill and not fixture:
        E.append(f"provenance: {ill} illustrative elements in a pipeline payload (must be 0)")
    elif ill:
        W.append(f"fixture: {ill} illustrative elements (shown only because run.mode is 'fixture')")

    # 9. Modelled-prevalence language must not appear anywhere (method not approved)
    txt = json.dumps(p).lower()
    for phrase in ("expected register", "register gap", "not yet diagnosed", "missing patients"):
        if phrase in txt:
            E.append(f"method: '{phrase}' used, but expected-prevalence modelling is not approved")

    # 10. Evidence associations need a rule in pipeline mode
    for k, a in live.items():
        e = (a.get("l2") or {}).get("evidence") or {}
        if not fixture and (e.get("associations") or e.get("no_relationship")) and not e.get("rule_version"):
            E.append(f"area {k}: evidence associations without a rule_version")
    return E, W

if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        E, W = lint(json.loads(pathlib.Path(f).read_text()))
        print(f"== {f}")
        for e in E: print("  ERROR ", e)
        for w in W: print("  warn  ", w)
        bad += len(E)
    sys.exit(1 if bad else 0)
