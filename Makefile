PY ?= python3
PAYLOAD ?= payloads/demo-kilburn-park.json

.PHONY: fixture lint static all
fixture:
	$(PY) payloads/build_demo_payload.py

lint:
	$(PY) tools/lint_payload.py payloads/*.json

static:
	$(PY) tools/build_static.py $(PAYLOAD)
	$(PY) tools/build_static.py $(PAYLOAD) --demo

all: fixture lint static
