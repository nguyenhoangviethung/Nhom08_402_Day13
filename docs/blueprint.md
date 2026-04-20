# Day 13 Observability Lab - Bao cao nhom (Blueprint)

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
- Blueprint report co du thanh vien: PASS

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- Correlation ID propagation, enrichment, PII scrubbing: PASS theo `scripts/validate_logs.py`.
- Trace live du metadata (`feature`, `request_id`, `session_id`, `user_id_hash`) tren Langfuse.
- Span hierarchy da instrument:
  - Root span: `chat-<feature>`
  - Retrieval span: `Retrieve_Context`
  - Generation span: `LLM_Generate`

Evidence:
- Trace list (live): ![Trace List](static/tracing.png)
- Sessions monitoring: ![Langfuse Sessions](static/sessions.png)

Trace hierarchy explanation:
- Root span `chat-qa` dai dien cho request chat.
- Child span `Retrieve_Context` giup khoanh vung bottleneck retrieval.
- Child generation `LLM_Generate` ghi usage token/model de debug chi phi va chat luong.
- Luong debug thuc te: Metrics -> Traces -> Logs.

### 3.2 Dashboard & SLOs
Dashboard duoc xay dung va doi chieu theo SLO:
- Latency panel: p50/p95/p99, threshold line theo `latency_p95_ms <= 3000`.
- Usage panel: trace count, observation count, trend theo thoi gian.
- Cost panel: tong chi phi, chi phi theo model/use case.

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
Alert rules da cau hinh du 3 muc va co runbook:
- `high_latency_p95`
- `high_error_rate`
- `cost_budget_spike`

Runtime latest:
- total alerts: 3
- firing: 0
- runbook anchors hoat dong trong `docs/alerts.md`

Runbook links:
- `docs/alerts.md#1-high-latency-p95`
- `docs/alerts.md#2-high-error-rate`
- `docs/alerts.md#3-cost-budget-spike`

---

## 4. Incident Response (Group)
- Scenario name: `tool_fail`
- Symptoms observed:
  - `error_rate_pct` tang vuot nguong 5%
  - Alert `high_error_rate` firing trong giai doan test incident
- Root cause proved by:
  - Log co `error_type=RuntimeError` khi bat incident `tool_fail`
  - Trace cho thay request fail trong pipeline retrieval/tool
- Fix action:
  - Tat incident `tool_fail`
  - Chay load test on dinh de reset error rate ve nguong an toan
- Preventive measure:
  - Bat buoc chay gate truoc demo: `python scripts/member_f_gate.py --check-member-de-runtime --strict`
  - Duy tri validator theo role (`validate_member_c/d/e.py`) trong quy trinh freeze ky thuat

---

## 5. Individual Contributions & Evidence

### Member A - Mai Viet Hoang
Tasks completed:
- Trien khai Correlation ID middleware, bind contextvars, enrichment field cho log API.
- Trien khai va harden PII scrubbing pipeline (`app/pii.py`, `app/logging_config.py`).
Evidence:
- Bao cao ca nhan: `docs/individual/mai_viet_hoang_2a202600476.md`
- Files: `app/middleware.py`, `app/pii.py`, `app/logging_config.py`, `app/main.py`

### Member B - Nguyen Thi Huong Giang
Tasks completed:
- Hoan thien Langfuse tracing, metadata/tags, root-child observations.
- Xu ly van de export trace va dong bo host env.
Evidence:
- Bao cao ca nhan: `docs/individual/nguyenhuonggiang.md`
- Files: `app/tracing.py`, `app/agent.py`, `app/mock_llm.py`, `app/mock_rag.py`

### Member C - Le Hong Anh
Tasks completed:
- Trien khai danh gia SLO, alert parser/evaluator, mo endpoint `/slo` va `/alerts`.
- Bo sung test cho SLO + alerts.
Evidence:
- Bao cao ca nhan: `docs/individual/Le_Hong_Anh.md`
- Files: `app/slo_alerts.py`, `app/main.py`, `tests/test_slo_alerts.py`

### Member D - Hoang Duc Hung
Tasks completed:
- Nang cap load test script (concurrency/repeat/percentile/throughput).
- Nang cap inject incident script va quy trinh before/after.
Evidence:
- Bao cao ca nhan: `docs/individual/HoangDucHung-report.md`
- Files: `scripts/load_test.py`, `scripts/inject_incident.py`, `data/incidents.json`

### Member E - Nguyen Thanh Binh
Tasks completed:
- QA validation logs 100/100 va thu thap evidence dashboard/tracing.
- Xac dinh panel mapping va doi chieu metrics runtime.
Evidence:
- Bao cao ca nhan: `docs/individual/NguyenThanhBinh.md`
- Files: `docs/dashboard-spec.md`, `docs/grading-evidence.md`, `docs/static/*`

### Member F - Nguyen Hoang Viet Hung
Tasks completed:
- So huu blueprint, gate demo, va dieu phoi handover D/E khi co backlog.
- Mo rong validator theo member va dong bo tai lieu/guide de chot demo an toan.
Evidence:
- Bao cao ca nhan: `docs/individual/nguyenhoangviethung.md`
- Files: `scripts/member_f_gate.py`, `scripts/validate_member_d.py`, `scripts/validate_member_e.py`, `guide.md`

---

## 6. Bonus Items
- Bonus automation (+2):
  - Da xay bo script gate va validator theo role:
    - `scripts/validate_logs.py`
    - `scripts/validate_member_c.py`
    - `scripts/validate_member_d.py`
    - `scripts/validate_member_e.py`
    - `scripts/member_f_gate.py`
- Bonus cost governance (+3, de xuat):
  - Co panel cost va alert cost spike.
  - Daily cost runtime hien tai: $0.1231 (< $2.5/day)

---

## 7. Demo Script (8-10 phut)
1. Health + quality gate (`validate_logs`, `validate_member_d/e`, trace count).
2. Show tracing list va 1 trace de giai thich hierarchy.
3. Show dashboard latency/usage/cost va doi chieu SLO table.
4. Show alerts status + runbook.
5. Trinh bay 1 incident RCA theo flow Metrics -> Traces -> Logs.
6. Ket luan theo passing criteria va dong gop tung member.

---

## 8. Ket luan
Nhom da hoan thien day du 6 tru cot observability (Logs, Traces, Metrics, SLO, Alerts, Runbook/Report), co bo validation tu dong truoc demo, va co evidence thuc te tren Langfuse + dashboard. Trang thai hien tai phu hop muc tieu dat diem cao theo rubric 60/40.
