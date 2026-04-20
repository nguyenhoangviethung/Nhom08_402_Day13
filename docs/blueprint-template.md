# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Nhom08_402_13
- [REPO_URL]: https://github.com/VinUni-AI20k/Lab13-Observability
- [MEMBERS]:
  - Member A: Mai Viet Hoang | Role: Logging & PII
  - Member B: Nguyen Thi Huong Giang | Role: Tracing & Enrichment
  - Member C: Le Hong Anh | Role: SLO & Alerts
  - Member D: Hoang Duc Hung | Role: Load Test & Incident Injection
  - Member E: Nguyen Thanh Binh | Role: Dashboard & Evidence
  - Member F: Nguyen Hoang Viet Hung | Role: Blueprint & Demo Lead

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 115
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/static/tracing.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/static/tracing.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/static/sessions.png
- [TRACE_WATERFALL_EXPLANATION]: Root span `chat-qa` bao bọc toàn bộ request, sau đó child span `Retrieve_Context` và generation `LLM_Generate` giúp khoanh vùng latency/cost và root cause theo flow Metrics -> Traces -> Logs.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/static/dashboard_latency.png, docs/static/dashboard_usage.png, docs/static/dashboard_cost.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 170ms |
| Error Rate | < 2% | 28d | 1.754% |
| Cost Budget | < $2.5/day | 1d | $0.1231 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/static/dashboard_latency.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: tool_fail
- [SYMPTOMS_OBSERVED]: Error rate tăng > 5%, alert `high_error_rate` firing trong cửa sổ test incident; request fail với `RuntimeError`.
- [ROOT_CAUSE_PROVED_BY]: Log `request_failed` có `error_type=RuntimeError`, trace fail trong pipeline retrieval/tool khi incident `tool_fail` được bật.
- [FIX_ACTION]: Tắt `tool_fail`, bổ sung runbook thao tác rollback/toggle, chạy lại load test ổn định để đưa error_rate về ngưỡng an toàn.
- [PREVENTIVE_MEASURE]: Bắt buộc chạy gate `python scripts/member_f_gate.py --check-member-de-runtime --strict` trước demo và theo dõi alerts real-time.

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: Mai Viet Hoang - triển khai middleware correlation ID, log enrichment context, PII scrubber pipeline và hardening logging flow.
- [EVIDENCE_LINK]: docs/individual/mai_viet_hoang_2a202600476.md

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: Nguyen Thi Huong Giang - hoàn thiện tracing Langfuse, metadata/tags, trace hierarchy, xử lý export/no-op issue.
- [EVIDENCE_LINK]: docs/individual/nguyenhuonggiang.md

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: Le Hong Anh - triển khai SLO evaluator, alert evaluator, endpoint `/slo` và `/alerts`, bổ sung unit tests.
- [EVIDENCE_LINK]: docs/individual/Le_Hong_Anh.md

### [MEMBER_D_NAME]
- [TASKS_COMPLETED]: Hoang Duc Hung - nâng cấp load test script, incident injection script và quy trình before/after incident.
- [EVIDENCE_LINK]: docs/individual/HoangDucHung-report.md

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: Nguyen Thanh Binh - QA validation logs 100/100, dashboard/evidence mapping, tổng hợp bằng chứng nộp bài.
- [EVIDENCE_LINK]: docs/individual/NguyenThanhBinh.md

### [MEMBER_F_NAME]
- [TASKS_COMPLETED]: Nguyen Hoang Viet Hung - sở hữu group blueprint, điều phối dry-run, tích hợp gate liên member và tiếp quản D/E backlog khi cần.
- [EVIDENCE_LINK]: docs/individual/nguyenhoangviethung.md

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Cost governance qua panel cost + alert spike; daily cost runtime $0.1231 (< $2.5/day).
- [BONUS_AUDIT_LOGS]: Tracking request lifecycle qua structured JSON logs + correlation ID; evidence từ `data/logs.jsonl` và `scripts/validate_logs.py`.
- [BONUS_CUSTOM_METRIC]: Bộ validator tự động theo role (`validate_member_c/d/e.py`) + `member_f_gate.py` cho pre-demo QA.
