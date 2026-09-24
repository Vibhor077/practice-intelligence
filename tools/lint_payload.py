"""
Semantic checks the JSON schema cannot express. These encode product rules, so a payload
that passes the schema can still be refused here. Run in CI on every generated payload.

  python tools/lint_payload.py payloads/*.json          # exit 1 on any ERROR
"""
import json, sys, pathlib

def lint(p):
    E, W = [], []
    areas = p["areas"]
    live = {k: a for k, a in areas.items() if a["status"] != "in_development"}

    # 1. Every area reference resolves
    refs = [("assessment", l["area"]) for l in p["assessment"]["lines"]] + [("attention", p["attention"]["area"])] \
         + [("changes", c["area"]) for c in p["changes"]["items"]] + [("access_measures", m["area"]) for m in p["access_measures"]["items"]]
    for where, r in refs:
        if r not in areas: E.append(f"{where}: unknown area '{r}'")
    for k, a in areas.items():
        if a["group"] not in {g["id"] for g in p["groups"]}: E.append(f"area {k}: unknown group '{a['group']}'")

    # 2. The attention panel points at the highest-priority live area (v8 bug: it did not)
    top = max(live, key=lambda k: live[k]["priority"])
    if p["attention"]["area"] != top:
        E.append(f"attention: points at '{p['attention']['area']}' but highest priority is '{top}'")
    if p["attention"]["metric"]["prov"] != "real":
        E.append("attention: headline metric must be real data")

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
            if rank.get(a["status"], 0) > rank.get(b["status"], 0) and a["priority"] < b["priority"]:
                W.append(f"priority: '{k}' ({a['status']}) scores below '{k2}' ({b['status']})")

    # 6. In-development areas carry no numbers
    for k, a in areas.items():
        if a["status"] == "in_development" and any(x in a for x in ("metric", "card", "l2", "l3")):
            E.append(f"area {k}: in_development but carries figures")

    # 7. Changes are not padded: each must have >= 3 points to show a pattern
    for c in p["changes"]["items"]:
        if len(c["series"]) < 3: W.append(f"changes: '{c['label']}' has fewer than 3 points")

    # 8. Demo readiness: count illustrative values that would be hidden
    ill = json.dumps(p).count('"prov": "illustrative"')
    W.append(f"demo: {ill} illustrative elements will be hidden in real-data-only mode") if ill else None
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
