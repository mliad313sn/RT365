# Local developer entry points. CI runs the same targets (see .github/workflows/ci.yml).
PY ?= python3
export RT_ENV ?= sim
export PYTHONPATH := libs/core:services/market-data:services/strategy:services/backtest:services/portfolio:services/risk:services/compliance:services/approval:services/oms:services/execution:services/reconciliation:services/audit:services/killswitch:services/identity:mcp/servers:connectors/brokers:connectors/data-providers:observability:apps/web:test

.PHONY: install lint typecheck test evidence schemas policy-check sbom secret-scan certify-broker run-bff all

install:
	$(PY) -m pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

typecheck:
	$(PY) -m mypy libs services mcp connectors observability apps

test:
	$(PY) -m pytest

evidence: test
	$(PY) scripts/evidence_report.py
	$(PY) scripts/export_test_cases.py

schemas:
	$(PY) scripts/export_event_schemas.py --check

policy-check:
	$(PY) scripts/check_network_policies.py
	$(PY) scripts/verify_tool_registry.py

sbom:
	$(PY) scripts/generate_sbom.py

lock:
	$(PY) -m pip freeze --exclude-editable > requirements.lock.txt

security-scan:
	$(PY) -m bandit -q -r libs services mcp connectors observability apps -x test || true
	$(PY) -m pip_audit -r requirements.lock.txt || true

secret-scan:
	$(PY) scripts/secret_scan.py

certify-broker:
	$(PY) scripts/certify_broker.py

run-bff:
	uvicorn web_bff.app:create_app --factory --port 8080

all: lint typecheck schemas policy-check secret-scan test evidence
