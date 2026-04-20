# Alert Rules and Runbooks

Tài liệu này là runbook vận hành cho phần Member C (SLO + Alerts), được dùng để demo và xử lý sự cố trong bài chấm Day 13.

## Alert summary

| Alert name | Severity | Condition | Service impact | Owner |
|---|---|---|---|---|
| `high_latency_p95` | P2 | `latency_p95_ms > 5000 for 30m` | Trễ response, nguy cơ vỡ SLO latency | team-oncall |
| `high_error_rate` | P1 | `error_rate_pct > 5 for 5m` | User nhận lỗi 5xx, giảm reliability | team-oncall |
| `cost_budget_spike` | P2 | `hourly_cost_usd > 2x_baseline for 15m` | Vượt ngân sách AI cost | finops-owner |

Nguồn dữ liệu:
- Runtime metrics: `GET /metrics`
- SLO status: `GET /slo`
- Alert status: `GET /alerts`
- Trace triage: Langfuse Tracing/Sessions dashboards

---

## 1. High latency P95

- Severity: P2
- Trigger: `latency_p95_ms > 5000 for 30m`
- Primary SLI liên quan: `latency_p95_ms` (objective 3000ms)
- Impact:
  - Tail latency vượt ngưỡng cho một nhóm request
  - Có nguy cơ domino sang error rate nếu timeout tăng

### Triage checklist
1. Mở dashboard latency và xác nhận p95 tăng liên tục.
2. Mở trace list trong 1h gần nhất, sắp xếp theo latency.
3. So sánh span `Retrieve_Context` và `LLM_Generate` để khoanh vùng bottleneck.
4. Kiểm tra incident toggle `rag_slow` có đang bật hay không.

### Mitigation
- Cắt gọn query/prompt dài bất thường.
- Chuyển sang retrieval fallback.
- Giảm kích thước context/prompt template.
- Tăng timeout tạm thời trong luồng demo nếu cần.

### Verify recovery
- `latency_p95` quay về ngưỡng an toàn.
- Alert status chuyển từ `firing` sang `ok`.
- Trace mới cho thấy span bottleneck đã giảm.

---

## 2. High error rate

- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Primary SLI liên quan: `error_rate_pct` (objective 2%)
- Impact:
  - User nhận response lỗi
  - Suy giảm chất lượng demo và reliability

### Triage checklist
1. Nhóm logs theo `error_type` và `event=request_failed`.
2. Mở trace fail để tìm bước gây lỗi (tool/RAG/LLM/schema).
3. Đối chiếu với incident toggles (`tool_fail`) và thay đổi code gần nhất.

### Mitigation
- Tắt tool lỗi (`tool_fail`) và rollback thay đổi mới nhất nếu cần.
- Retry với fallback flow/model.
- Giảm concurrency để tránh hiệu ứng dây chuyền.

### Verify recovery
- `error_rate_pct` giảm dưới ngưỡng 5% cảnh báo và tiếp tục hướng tới objective 2%.
- Số request thành công tăng để ổn định p95.
- Alert `high_error_rate` trở lại `ok`.

---

## 3. Cost budget spike

- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Primary SLI liên quan: `daily_cost_usd` (objective < 2.5 USD/day)
- Impact:
  - Tăng burn rate
  - Rủi ro vượt ngân sách khi tải cao

### Triage checklist
1. Mở cost dashboard và xác nhận trend tăng bất thường.
2. Tách theo model/use case để tìm nguồn tăng chi phí.
3. Đối chiếu `tokens_in_total`/`tokens_out_total` để kiểm tra prompt inflation.
4. Kiểm tra incident `cost_spike` có đang bật trong buổi test hay không.

### Mitigation
- Rút gọn prompt và context.
- Route use case đơn giản sang model rẻ hơn.
- Bật prompt cache/reuse retrieval kết quả.

### Verify recovery
- `hourly_cost_usd` quay về baseline.
- Trend cost dashboard phẳng hơn, không có đột biến.
- Alert cost chuyển về `ok`.

---

## Response flow (Metrics -> Traces -> Logs)

1. Metrics phát hiện symptom (`/alerts`, dashboard).
2. Traces khoanh vùng span/feature gây ảnh hưởng.
3. Logs xác nhận root cause (`error_type`, payload preview, request_id).
4. Áp dụng fix.
5. Re-check metrics và alert để đóng sự cố.

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
- Có đủ 3 alert rules đang chạy.
- Mỗi alert có owner + runbook + triage/mitigation/verify.
- Alert status và evidence có thể trình bày live trong 2 phút.
