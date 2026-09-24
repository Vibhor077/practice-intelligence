# Practice Intelligence

A management view for English GP practices: what matters, why, where to look, and how the practice compares.

```
make fixture   # build the demo payload (Kilburn Park, v8 content)
make lint      # schema + product-rule checks
make static    # dist/E84000.html (placeholders shown) and dist/E84000-demo.html (real data only)
```

Open `dist/E84000.html` in a browser. Use the switch at the top right to go between placeholder mode and real-data-only mode.

- **Working with Claude Code:** read `CLAUDE.md` first, then `docs/BUILD_PLAN.md`. Each step has a ready prompt.
- **What changed from v8:** `docs/DESIGN_V9.md`
- **Engine ↔ renderer contract:** `schema/payload.schema.json`
- **Metric registry:** `registry/metrics.yaml`
