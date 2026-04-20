# Dashboard Spec (Completed - Team 08)

Bảng điều khiển này được thiết kế để theo dõi hiệu suất, chi phí và độ tin cậy của hệ thống AI Agent dựa trên dữ liệu từ `logs.jsonl` và Langfuse.

## 1. Latency P50/P95/P99
- **Mô tả:** Theo dõi thời gian phản hồi của hệ thống.
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** Trường `latency_ms` trong log.
- **Ngưỡng SLO:** < 500ms cho các request bình thường.

## 2. Traffic (Request Count)
- **Mô tả:** Tổng số lượng yêu cầu được gửi đến hệ thống.
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** Đếm các `x-request-id` duy nhất. 
- **Ghi chú:** Đã xác nhận 43 request thành công qua script validate.

## 3. Error Rate with Breakdown
- **Mô tả:** Tỉ lệ lỗi và phân loại lỗi (4xx, 5xx).
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** Trường `level` (info/error) và `status_code`.

## 4. Cost Over Time
- **Mô tả:** Theo dõi chi phí sử dụng API LLM theo thời gian thực.
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** Trường `cost_usd` trong log (ví dụ: 0.001539 USD/request).

## 5. Tokens In/Out
- **Mô tả:** Đo lường khối lượng dữ liệu đầu vào và đầu ra của mô hình AI.
- **Trạng thái:** [x] Hoàn thành.
- **Dữ liệu nguồn:** Trường `tokens_in` và `tokens_out`.

## 6. Quality Proxy (Security & Reliability)
- **Mô tả:** Đảm bảo dữ liệu nhạy cảm được bảo vệ và hệ thống hoạt động ổn định.
- **Trạng thái:** [x] Hoàn thành.
- **Chỉ số:** Tỉ lệ PII Scrubbing thành công (Đạt 100% dựa trên kết quả validate).

---

## Quality Bar Check
- [x] Khoảng thời gian mặc định: 1 giờ.
- [x] Tự động làm mới (Auto-refresh): Mỗi 30 giây.
- [x] Đã thiết lập ngưỡng SLO (Threshold).
- [x] Đơn vị đo lường rõ ràng (ms, USD, count).
- [x] Dashboard gọn gàng (6 panels).