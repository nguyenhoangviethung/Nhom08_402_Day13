# Alert Rules and Runbooks

Tai lieu nay la runbook van hanh cho phan Member C (SLO + Alerts), duoc dung de demo va xu ly su co trong bai cham Day 13.

## Alert summary

| Alert name | Severity | Condition | Service impact | Owner |
|---|---|---|---|---|
| `high_latency_p95` | P2 | `latency_p95_ms > 5000 for 30m` | Tre response, nguy co vo SLO latency | team-oncall |
| `high_error_rate` | P1 | `error_rate_pct > 5 for 5m` | User nhan loi 5xx, giam reliability | team-oncall |
| `cost_budget_spike` | P2 | `hourly_cost_usd > 2x_baseline for 15m` | Vuot ngan sach AI cost | finops-owner |

Nguon du lieu:
- Runtime metrics: `GET /metrics`
- SLO status: `GET /slo`
- Alert status: `GET /alerts`
- Trace triage: Langfuse Tracing/Sessions dashboards

---

## 1. High latency P95

- Severity: P2
- Trigger: `latency_p95_ms > 5000 for 30m`
- Primary SLI lien quan: `latency_p95_ms` (objective 3000ms)
- Impact:
  - Tail latency vuot nguong cho mot nhom request
  - Co nguy co domino sang error rate neu timeout tang

### Triage checklist
1. Mo dashboard latency va xac nhan p95 tang lien tuc.
2. Mo trace list trong 1h gan nhat, sap xep theo latency.
3. So sanh span `Retrieve_Context` va `LLM_Generate` de khoanh vung bottleneck.
4. Kiem tra incident toggle `rag_slow` co dang bat hay khong.

### Mitigation
- Cat gon query/prompt dai bat thuong.
- Chuyen sang retrieval fallback.
- Giam kich thuoc context/prompt template.
- Tang timeout tam thoi trong luong demo neu can.

### Verify recovery
- `latency_p95` quay ve nguong an toan.
- Alert status chuyen tu `firing` sang `ok`.
- Trace moi cho thay span bottleneck da giam.

---

## 2. High error rate

- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Primary SLI lien quan: `error_rate_pct` (objective 2%)
- Impact:
  - User nhan response loi
  - Suy giam chat luong demo va reliability

### Triage checklist
1. Nhom logs theo `error_type` va `event=request_failed`.
2. Mo trace fail de tim buoc gay loi (tool/RAG/LLM/schema).
3. Doi chieu voi incident toggles (`tool_fail`) va thay doi code gan nhat.

### Mitigation
- Tat tool loi (`tool_fail`) va rollback thay doi moi nhat neu can.
- Retry voi fallback flow/model.
- Giam concurrency de tranh hieu ung day chuyen.

### Verify recovery
- `error_rate_pct` giam duoi nguong 5% canh bao va tiep tuc huong toi objective 2%.
- So request thanh cong tang de on dinh p95.
- Alert `high_error_rate` tro lai `ok`.

---

## 3. Cost budget spike

- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Primary SLI lien quan: `daily_cost_usd` (objective < 2.5 USD/day)
- Impact:
  - Tang burn rate
  - Ruui ro vuot ngan sach khi tai cao

### Triage checklist
1. Mo cost dashboard va xac nhan trend tang bat thuong.
2. Tach theo model/use case de tim nguon tang chi phi.
3. Doi chieu `tokens_in_total`/`tokens_out_total` de kiem tra prompt inflation.
4. Kiem tra incident `cost_spike` co dang bat trong buoi test hay khong.

### Mitigation
- Rut gon prompt va context.
- Route use case don gian sang model re hon.
- Bat prompt cache/reuse retrieval ket qua.

### Verify recovery
- `hourly_cost_usd` quay ve baseline.
- Trend cost dashboard phang hon, khong co dot bien.
- Alert cost chuyen ve `ok`.

---

## Response flow (Metrics -> Traces -> Logs)

1. Metrics phat hien symptom (`/alerts`, dashboard).
2. Traces khoanh vung span/feature gay anh huong.
3. Logs xac nhan root cause (`error_type`, payload preview, request_id).
4. Ap dung fix.
5. Re-check metrics va alert de dong su co.

---

## Demo commands (quick copy)

```bash
curl -s http://127.0.0.1:8000/metrics | python -m json.tool
curl -s http://127.0.0.1:8000/slo | python -m json.tool
curl -s http://127.0.0.1:8000/alerts | python -m json.tool
python scripts/inject_incident.py --status
python scripts/load_test.py --concurrency 5 --repeat 1
```

## Definition of done (alerts)
- Co du 3 alert rules dang chay.
- Moi alert co owner + runbook + triage/mitigation/verify.
- Alert status va evidence co the trinh bay live trong 2 phut.
