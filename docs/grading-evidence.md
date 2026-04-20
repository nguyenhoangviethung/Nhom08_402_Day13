# Evidence Collection Sheet (Final)

Tai lieu nay tong hop bang chung de nop bao cao nhom, dong bo voi rubric 60/40 va bo validator.

## 1. Required evidence matrix

| Requirement | Status | Owner | Evidence |
|---|---|---|---|
| Langfuse trace list with >= 10 traces | [x] | Member B (fallback F) | ![Trace List](static/tracing.png) |
| One full trace waterfall / trace hierarchy | [x] | Member B (fallback F) | ![Sessions and trace hierarchy](static/sessions.png) |
| JSON logs showing correlation_id | [x] | Member A/E | ![Tracing with request metadata](static/tracing.png) |
| Log line with PII redaction | [x] | Member A/E | ![Redaction evidence in trace input](static/tracing.png) |
| Dashboard with 6 panels | [x] | Member E (fallback F) | ![Latency](static/dashboard_latency.png), ![Usage](static/dashboard_usage.png), ![Cost](static/dashboard_cost.png) |
| Alert rules with runbook link | [x] | Member C (fallback F) | `docs/alerts.md`, `config/alert_rules.yaml`, runtime `GET /alerts` |
| Validation results summary | [x] | Member F | `scripts/validate_logs.py`, `scripts/validate_member_c.py`, `scripts/validate_member_d.py` |

## 2. Runtime command evidence (copy/paste)

```bash
python scripts/validate_logs.py
curl -s http://127.0.0.1:8000/slo | python -m json.tool
curl -s http://127.0.0.1:8000/alerts | python -m json.tool
set -a && source .env && set +a && npx -y langfuse-cli api traces list --limit 1
```

Current highlights used in report:
- Log score: 100/100
- PII leaks: 0
- Total traces (live): 115
- SLO overall: pass
- Alerts firing: 0

## 3. D/E to F handover rule
- Neu `scripts/validate_member_d.py` hoac `scripts/validate_member_e.py` FAIL truoc demo: Member F tiep quan backlog.
- Member F phai ghi ro takeover trong `docs/blueprint.md` va phan Member F trong report.
- Sau handover, bat buoc chay lai gate tong:

```bash
python scripts/member_f_gate.py --check-member-de-runtime --strict
```

## 4. Optional bonus evidence
- Incident before/after fix (metrics + traces + logs theo cung request flow).
- Cost comparison before/after stabilization.
- Automation proof (validator scripts per member + pre-demo gate).

## 5. Final submission checklist
- [x] Co du evidence logs/traces/dashboard/alerts.
- [x] Co runbook link hoat dong.
- [x] Co command de tai hien ket qua.
- [x] Co fallback ownership neu D/E con backlog.
