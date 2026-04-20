# Day 13 Observability Lab - Báo cáo nhóm (Blueprint)

## 1. Team Metadata
- Group name: Nhom08_402_13
- Repository: https://github.com/VinUni-AI20k/Lab13-Observability
- Branch demo: giang
- Members:
  - Member A: Mai Viet Hoang | Role: Logging & PII
  - Member B: Nguyen Thi Huong Giang | Role: Tracing & Enrichment
  - Member C: Le Hong Anh | Role: SLO & Alerts
  - Member D: Hoang Duc Hung | Role: Load Test & Incident Injection
  - Member E: Nguyen Thanh Binh | Role: Dashboard & Evidence
  - Member F: Nguyen Hoang Viet Hung | Role: Blueprint & Demo Lead

---

## 2. Group Performance (Auto-Verified)
- VALIDATE_LOGS_FINAL_SCORE: 100/100
- TOTAL_TRACES_COUNT (Langfuse live): 115
- PII_LEAKS_FOUND: 0
- Runtime snapshot (latest):
  - traffic: 57
  - latency_p95: 170 ms
  - error_rate_pct: 1.754%
  - daily_cost_usd: 0.1231
  - quality_avg: 0.8702

### Passing Criteria Check
- Log score >= 80: PASS (100/100)
- Trace count >= 10: PASS (115)
- Dashboard 6 panels: PASS (latency, usage, cost, sessions, tracing operations)
- Blueprint report có đủ thành viên: PASS

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- Correlation ID propagation, enrichment, PII scrubbing: PASS theo `scripts/validate_logs.py`.
- Trace live đủ metadata (`feature`, `request_id`, `session_id`, `user_id_hash`) trên Langfuse.
- Span hierarchy đã instrument:
  - Root span: `chat-<feature>`
  - Retrieval span: `Retrieve_Context`
  - Generation span: `LLM_Generate`

Evidence:
- Trace list (live): ![Trace List](static/tracing.png)
- Sessions monitoring: ![Langfuse Sessions](static/sessions.png)

Trace hierarchy explanation:
- Root span `chat-qa` đại diện cho request chat.
- Child span `Retrieve_Context` giúp khoanh vùng bottleneck retrieval.
- Child generation `LLM_Generate` ghi usage token/model để debug chi phí và chất lượng.
- Luồng debug thực tế: Metrics -> Traces -> Logs.

### 3.2 Dashboard & SLOs
Dashboard được xây dựng và đối chiếu theo SLO:
- Latency panel: p50/p95/p99, threshold line theo `latency_p95_ms <= 3000`.
- Usage panel: trace count, observation count, trend theo thời gian.
- Cost panel: tổng chi phí, chi phí theo model/use case.

Evidence:
- Latency dashboard: ![Dashboard Latency](static/dashboard_latency.png)
- Usage dashboard: ![Dashboard Usage](static/dashboard_usage.png)
- Cost dashboard: ![Dashboard Cost](static/dashboard_cost.png)

SLO table (runtime latest):

| SLI | Target | Window | Current Value | Status |
|---|---:|---|---:|---|
| Latency P95 | < 3000ms | 28d | 170ms | PASS |
| Error Rate | < 2% | 28d | 1.754% | PASS |
| Cost Budget | < $2.5/day | 1d | $0.1231 | PASS |
| Quality Score Avg | >= 0.75 | 28d | 0.8702 | PASS |

### 3.3 Alerts & Runbook
Alert rules đã cấu hình đủ 3 mục và có runbook:
- `high_latency_p95`
- `high_error_rate`
- `cost_budget_spike`

Runtime latest:
- total alerts: 3
- firing: 0
- runbook anchors hoạt động trong `docs/alerts.md`

Runbook links:
- `docs/alerts.md#1-high-latency-p95`
- `docs/alerts.md#2-high-error-rate`
- `docs/alerts.md#3-cost-budget-spike`

---

## 4. Incident Response (Group)
- Scenario name: `tool_fail`
- Symptoms observed:
  - `error_rate_pct` tăng vượt ngưỡng 5%
  - Alert `high_error_rate` firing trong giai đoạn test incident
- Root cause proved by:
  - Log có `error_type=RuntimeError` khi bật incident `tool_fail`
  - Trace cho thấy request fail trong pipeline retrieval/tool
- Fix action:
  - Tắt incident `tool_fail`
  - Chạy load test ổn định để reset error rate về ngưỡng an toàn
- Preventive measure:
  - Bắt buộc chạy gate trước demo: `python scripts/member_f_gate.py --check-member-de-runtime --strict`
  - Duy trì validator theo role (`validate_member_c/d/e.py`) trong quy trình freeze kỹ thuật

---

## 5. Individual Contributions & Evidence

### Member A - Mai Viet Hoang
Tasks completed:
- Triển khai Correlation ID middleware, bind contextvars, enrichment field cho log API.
- Triển khai và harden PII scrubbing pipeline (`app/pii.py`, `app/logging_config.py`).
Evidence:
- Báo cáo cá nhân: `docs/individual/mai_viet_hoang_2a202600476.md`
- Files: `app/middleware.py`, `app/pii.py`, `app/logging_config.py`, `app/main.py`

### Member B - Nguyen Thi Huong Giang
Tasks completed:
- Hoàn thiện Langfuse tracing, metadata/tags, root-child observations.
- Xử lý vấn đề export trace và đồng bộ host env.
Evidence:
- Báo cáo cá nhân: `docs/individual/nguyenhuonggiang.md`
- Files: `app/tracing.py`, `app/agent.py`, `app/mock_llm.py`, `app/mock_rag.py`

### Member C - Le Hong Anh
Tasks completed:
- Triển khai đánh giá SLO, alert parser/evaluator, mở endpoint `/slo` và `/alerts`.
- Bổ sung test cho SLO + alerts.
Evidence:
- Báo cáo cá nhân: `docs/individual/Le_Hong_Anh.md`
- Files: `app/slo_alerts.py`, `app/main.py`, `tests/test_slo_alerts.py`

### Member D - Hoang Duc Hung
Tasks completed:
- Nâng cấp load test script (concurrency/repeat/percentile/throughput).
- Nâng cấp inject incident script và quy trình before/after.
Evidence:
- Báo cáo cá nhân: `docs/individual/HoangDucHung-report.md`
- Files: `scripts/load_test.py`, `scripts/inject_incident.py`, `data/incidents.json`

### Member E - Nguyen Thanh Binh
Tasks completed:
- QA validation logs 100/100 và thu thập evidence dashboard/tracing.
- Xác định panel mapping và đối chiếu metrics runtime.
Evidence:
- Báo cáo cá nhân: `docs/individual/NguyenThanhBinh.md`
- Files: `docs/dashboard-spec.md`, `docs/grading-evidence.md`, `docs/static/*`

### Member F - Nguyen Hoang Viet Hung
Tasks completed:
- Sở hữu blueprint, gate demo, và điều phối handover D/E khi có backlog.
- Mở rộng validator theo member và đồng bộ tài liệu/guide để chốt demo an toàn.
Evidence:
- Báo cáo cá nhân: `docs/individual/nguyenhoangviethung.md`
- Files: `scripts/member_f_gate.py`, `scripts/validate_member_d.py`, `scripts/validate_member_e.py`, `guide.md`

---

## 6. Bonus Items
- Bonus automation (+2):
  - Đã xây bộ script gate và validator theo role:
    - `scripts/validate_logs.py`
    - `scripts/validate_member_c.py`
    - `scripts/validate_member_d.py`
    - `scripts/validate_member_e.py`
    - `scripts/member_f_gate.py`
- Bonus cost governance (+3, đề xuất):
  - Có panel cost và alert cost spike.
  - Daily cost runtime hiện tại: $0.1231 (< $2.5/day)

---

## 7. Demo Script (8-10 phút)
1. Health + quality gate (`validate_logs`, `validate_member_d/e`, trace count).
2. Show tracing list và 1 trace để giải thích hierarchy.
3. Show dashboard latency/usage/cost và đối chiếu SLO table.
4. Show alerts status + runbook.
5. Trình bày 1 incident RCA theo flow Metrics -> Traces -> Logs.
6. Kết luận theo passing criteria và đóng góp từng member.

---

## 8. Kết luận
Nhóm đã hoàn thiện đầy đủ 6 trụ cột observability (Logs, Traces, Metrics, SLO, Alerts, Runbook/Report), có bộ validation tự động trước demo, và có evidence thực tế trên Langfuse + dashboard. Trạng thái hiện tại phù hợp mục tiêu đạt điểm cao theo rubric 60/40.
