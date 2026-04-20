# Dashboard Spec - Final (Nhom08_402_13)

Tài liệu này mô tả dashboard chính thức dùng để demo và chấm điểm, đồng bộ với rubric Day 13 và cấu hình SLO/Alerts trong hệ thống.

## A. Dashboard inventory (6 panels)

### 1) Latency (P50/P95/P99)
- Mục tiêu: theo dõi độ trễ tổng thể và tail-latency.
- Metric keys: `latency_p50`, `latency_p95`, `latency_p99`
- Unit: ms
- Threshold/SLO line: `latency_p95 <= 3000ms`
- Evidence screenshot: ![Latency Dashboard](static/dashboard_latency.png)

### 2) Traffic (Request volume)
- Mục tiêu: theo dõi lượng request để đối chiếu throughput và stress test.
- Metric keys: `traffic`
- Unit: count
- Nguồn: endpoint `/metrics` + load test output

### 3) Error Rate & Error Breakdown
- Mục tiêu: phát hiện suy giảm reliability.
- Metric keys: `error_rate_pct`, `total_errors`, `error_breakdown`
- Unit: % / count
- Threshold line: alert warning từ 5% (`high_error_rate`), objective SLO < 2%

### 4) Cost Over Time
- Mục tiêu: quản trị chi phí AI và phát hiện burn-rate bất thường.
- Metric keys: `hourly_cost_usd`, `daily_cost_usd`, `avg_cost_usd`
- Unit: USD
- Evidence screenshot: ![Cost Dashboard](static/dashboard_cost.png)

### 5) Token Usage (Input/Output)
- Mục tiêu: theo dõi token để tối ưu prompt và cost.
- Metric keys: `tokens_in_total`, `tokens_out_total`
- Unit: count

### 6) Quality/Security Proxy
- Mục tiêu: theo dõi chất lượng trả lời và an toàn dữ liệu.
- Metric keys: `quality_avg` + `pii_hits` (từ `scripts/validate_logs.py`)
- Unit: score / count

---

## B. Supporting dashboards/screens

- Tracing operations: ![Tracing](static/tracing.png)
- Usage management (trace/observation totals): ![Usage Dashboard](static/dashboard_usage.png)
- Sessions monitoring: ![Sessions](static/sessions.png)

---

## C. Mapping panel -> runtime source

| Panel | Runtime source | Formula/Meaning |
|---|---|---|
| Latency | `/metrics` | p50/p95/p99 trên `REQUEST_LATENCIES` |
| Traffic | `/metrics` | tổng số request đã record |
| Error | `/metrics` | `error_rate_pct = total_errors / traffic * 100` |
| Cost | `/metrics` | tổng và trung bình chi phí theo request |
| Tokens | `/metrics` | tổng token vào/ra của mô hình |
| Quality/Security | `/metrics` + `validate_logs.py` | `quality_avg` + PII leak count |

---

## D. Latest runtime snapshot (for report)

- traffic: 57
- latency_p95: 170 ms
- error_rate_pct: 1.754%
- daily_cost_usd: 0.1231
- tokens_in_total: 1973
- tokens_out_total: 7809
- quality_avg: 0.8702

Note: Snapshot được cập nhật sau khi chạy load test ổn định để phục vụ phần demo và báo cáo.

---

## E. Quality bar checklist

- [x] Đủ 6 panels theo rubric.
- [x] Có unit rõ ràng (ms, %, USD, count).
- [x] Có threshold/SLO line cho panel quan trọng.
- [x] Có evidence screenshot trong `docs/static`.
- [x] Có mapping metric key để đối chiếu với SLO/alerts.

## F. Demo sequence (dashboard section)

1. Mở `dashboard_latency.png` và giải thích SLO line 3000ms.
2. Mở `dashboard_usage.png` để chứng minh trace/observation volume.
3. Mở `dashboard_cost.png` để trình bày governance chi phí.
4. Đối chiếu với `/slo` và `/alerts` để kết luận hệ thống đang pass.