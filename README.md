# Day 13 Observability Lab - Nhom08_402_13

Final implementation repo for Monitoring, Logging, and Observability lab.

## Project status

System da hoan thanh cac tru cot observability:
- structured JSON logging
- correlation ID propagation
- PII scrubbing
- Langfuse tracing
- runtime metrics aggregation
- SLO + alert evaluation
- dashboard/evidence + group blueprint report

Latest verification snapshot:
- validate logs: 100/100
- live traces: 115
- PII leaks: 0
- SLO overall: pass

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Core verification commands

```bash
# Logging + PII
python scripts/validate_logs.py

# Validate Member C deliverables (SLO + Alerts)
python scripts/validate_member_c.py --check-runtime --strict

# Validate Member D deliverables (load test + incident injection)
python scripts/validate_member_d.py --check-runtime --strict

# Validate Member E deliverables (dashboard + evidence)
python scripts/validate_member_e.py --check-runtime --strict

# Member F final pre-demo gate
python scripts/member_f_gate.py --check-member-de-runtime --strict

# Optional: auto-fill group metrics in docs/blueprint-template.md
python scripts/member_f_gate.py --write-group-metrics
```

## Demo support commands

```bash
# Generate traffic
python scripts/load_test.py --concurrency 5 --repeat 2

# Inject/rollback incidents
python scripts/inject_incident.py --scenario rag_slow
python scripts/inject_incident.py --scenario rag_slow --disable

# Runtime inspection
curl -s http://127.0.0.1:8000/health | python -m json.tool
curl -s http://127.0.0.1:8000/metrics | python -m json.tool
curl -s http://127.0.0.1:8000/slo | python -m json.tool
curl -s http://127.0.0.1:8000/alerts | python -m json.tool
```

## Reports and evidence

- Group report: `docs/blueprint.md`
- Blueprint template (machine-parsed format): `docs/blueprint-template.md`
- Alerts runbook: `docs/alerts.md`
- Dashboard specification: `docs/dashboard-spec.md`
- Evidence matrix: `docs/grading-evidence.md`
- Individual reports: `docs/individual/`
- Screenshot assets: `docs/static/`

## Repo map

```text
app/
  main.py                FastAPI app
  agent.py               core agent pipeline
  logging_config.py      structlog config
  middleware.py          correlation ID middleware
  pii.py                 scrubbing helpers
  tracing.py             Langfuse helpers
  schemas.py             request/response/log models
  metrics.py             in-memory metrics helpers
  incidents.py           toggles for injected failures
  mock_llm.py            deterministic fake LLM
  mock_rag.py            deterministic fake retrieval
config/
  slo.yaml               starter SLOs
  alert_rules.yaml       starter alerts
  logging_schema.json    expected log schema
scripts/
  load_test.py           generate requests
  inject_incident.py     flip incident toggles
  validate_logs.py       schema checks for logs
  validate_member_d.py   verify load test + incident injection readiness
  validate_member_e.py   verify dashboard + evidence readiness
  validate_member_c.py   verify SLO + alerts readiness
  member_f_gate.py       pre-demo quality gate for report/demo owner
data/
  sample_queries.jsonl   requests for testing
  expected_answers.jsonl starter quality checks
  incidents.json         scenario descriptions
  logs.jsonl             app output target
  audit.jsonl            optional audit log output

docs/
  blueprint.md           final group report (filled)
  blueprint-template.md  team submission template
  alerts.md              runbook + alert worksheet
  dashboard-spec.md      6-panel dashboard specification + evidence mapping
  grading-evidence.md    submission evidence matrix
  individual/            member reports
  static/                screenshot assets for report
```

## Team role suggestion

- Member A: logging + PII
- Member B: tracing + tags
- Member C: SLO + alerts
- Member D: load test + incident injection
- Member E: dashboard + evidence
- Member F: blueprint + demo lead

## Grading policy (60/40 Split)

Your final grade is calculated as follows:

1. **Group Score (60%)**: 
   - **Technical Implementation (30 pts)**: Verified by `validate_logs.py` and live system state.
   - **Incident Response (10 pts)**: Accuracy of your root cause analysis in the report.
   - **Live Demo (20 pts)**: Team presentation and system demonstration.
2. **Individual Score (40%)**:
   - **Individual Report (20 pts)**: Quality of your specific contributions in `docs/blueprint-template.md`.
   - **Git Evidence (20 pts)**: Traceable work via commits and code ownership.

**Passing criteria**:
- `validate_logs` >= 80 (target 100)
- Langfuse traces >= 10
- Dashboard du 6 panels va co threshold line
- Blueprint/report day du thanh vien + evidence

## Repository
- GitHub: https://github.com/VinUni-AI20k/Lab13-Observability
# Nhom08_402_13
