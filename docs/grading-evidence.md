# Evidence Collection Sheet (Final)

Tài liệu này tổng hợp bằng chứng để nộp báo cáo nhóm, đồng bộ với rubric 60/40 và bộ validator.

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
- Nếu `scripts/validate_member_d.py` hoặc `scripts/validate_member_e.py` FAIL trước demo: Member F tiếp quản backlog.
- Member F phải ghi rõ takeover trong `docs/blueprint.md` và phần Member F trong report.
- Sau handover, bắt buộc chạy lại gate tổng:

```bash
python scripts/member_f_gate.py --check-member-de-runtime --strict
```

## 4. Optional bonus evidence
- Incident before/after fix (metrics + traces + logs theo cùng request flow).
- Cost comparison before/after stabilization.
- Automation proof (validator scripts per member + pre-demo gate).

## 5. Final submission checklist
- [x] Có đủ evidence logs/traces/dashboard/alerts.
- [x] Có runbook link hoạt động.
- [x] Có command để tái hiện kết quả.
- [x] Có fallback ownership nếu D/E còn backlog.
