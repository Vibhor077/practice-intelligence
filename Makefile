PY ?= uv run python
PAYLOAD ?= payloads/demo-kilburn-park.json

.PHONY: fixture lint static all
fixture:
	$(PY) payloads/build_demo_payload.py

lint:
	$(PY) tools/lint_payload.py payloads/*.json

static:
	$(PY) tools/build_static.py $(PAYLOAD)

all: fixture lint static
