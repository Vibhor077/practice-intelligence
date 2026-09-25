"""
Render one practice payload into a self-contained HTML page.

  python tools/build_static.py payloads/demo-kilburn-park.json               # -> dist/<ods>.html (real data only)
  python tools/build_static.py payloads/demo-kilburn-park.json --fragment    # body fragment (for artifact hosting)

Validates the payload against schema/payload.schema.json first; refuses to build an invalid payload.
"""
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("payload")
    ap.add_argument("--fragment", action="store_true", help="emit body fragment without <html> wrapper")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    data = json.loads(pathlib.Path(a.payload).read_text())
    try:
        import jsonschema
        schema = json.loads((ROOT / "schema/payload.schema.json").read_text())
        errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errs:
            for e in errs[:20]:
                print(f"SCHEMA  {'/'.join(map(str, e.path))}: {e.message}", file=sys.stderr)
            sys.exit(1)
    except ImportError:
        print("warning: jsonschema not installed; skipping validation", file=sys.stderr)

    tpl = (ROOT / "web/app.html").read_text()
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    tag = '<script type="application/json" id="pi-payload">'
    body = tpl.replace(tag + "__PAYLOAD__", tag + blob)

    if a.fragment:
        html = body
    else:
        html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                '<style>[hidden]{display:none!important}</style></head><body>\n' + body + "\n</body></html>")
    out = pathlib.Path(a.out) if a.out else ROOT / "dist" / f"{data['practice']['ods_code']}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print("wrote", out, f"({len(html)//1024} KB)")

if __name__ == "__main__":
    main()
