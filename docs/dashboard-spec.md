# Dashboard Spec (Completed - Team 08)

Bảng điều khiển này được thiết kế để theo dõi hiệu suất, chi phí và độ tin cậy của hệ thống AI Agent dựa trên dữ liệu từ `logs.jsonl` và Langfuse.

## 1. Latency P50/P95/P99
- **Mô tả:** Theo dõi thời gian phản hồi của hệ thống.
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** Trường `latency_ms` trong log.
- **Ngưỡng SLO line:** `latency_p95_ms <= 3000ms` (đồng bộ với `config/slo.yaml`).

## 2. Traffic (Request Count)
- **Mô tả:** Tổng số lượng yêu cầu được gửi đến hệ thống.
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** Đếm các `x-request-id` duy nhất. 
- **Metric runtime:** `traffic` từ endpoint `/metrics`.

## 3. Error Rate with Breakdown
- **Mô tả:** Tỉ lệ lỗi và phân loại lỗi (4xx, 5xx).
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** `error_rate_pct`, `total_errors`, `error_breakdown` từ endpoint `/metrics`.

## 4. Cost Over Time
- **Mô tả:** Theo dõi chi phí sử dụng API LLM theo thời gian thực.
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** `daily_cost_usd`, `hourly_cost_usd`, `avg_cost_usd`.

## 5. Tokens In/Out
- **Mô tả:** Đo lường khối lượng dữ liệu đầu vào và đầu ra của mô hình AI.
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** `tokens_in_total` và `tokens_out_total`.

## 6. Quality Proxy (Security & Reliability)
- **Mô tả:** Đảm bảo dữ liệu nhạy cảm được bảo vệ và hệ thống hoạt động ổn định.
- **Trạng thái:** [x] Hoàn thành.
- **Chỉ số:** `quality_avg` + tỉ lệ PII Scrubbing thành công (Đạt 100% dựa trên kết quả validate).

---

## Mapping panel -> metric key
- Latency panel: `latency_p50`, `latency_p95`, `latency_p99` (unit: ms).
- Traffic panel: `traffic` (unit: count).
- Error panel: `error_rate_pct`, `total_errors`, `error_breakdown` (unit: %/count).
- Cost panel: `daily_cost_usd`, `hourly_cost_usd`, `avg_cost_usd` (unit: USD).
- Tokens panel: `tokens_in_total`, `tokens_out_total` (unit: count).
- Quality/Security panel: `quality_avg`, `pii_hits` từ `scripts/validate_logs.py` (unit: score/count).

---

## Quality Bar Check
- [x] Khoảng thời gian mặc định: 1 giờ.
- [x] Tự động làm mới (Auto-refresh): Mỗi 30 giây.
- [x] Đã thiết lập ngưỡng SLO (Threshold).
- [x] Đơn vị đo lường rõ ràng (ms, USD, count).
- [x] Dashboard gọn gàng (6 panels).