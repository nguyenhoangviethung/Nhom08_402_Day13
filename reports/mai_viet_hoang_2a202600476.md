# Báo cáo Cá nhân: Member A - Logging & PII
**Thành viên:** Mai Việt Hoàng (2a202600476)
**Vai trò:** Member A - Chuyên trách Hệ thống Logging và Bảo vệ dữ liệu nhạy cảm (PII)
**Nhánh Git:** `hoangdzai`

---

## 1. Các thành tựu kỹ thuật đã đạt được

### 1.1. Triển khai Hệ thống Định danh Luồng (Correlation ID Propagation)
- **Tập tin:** `app/middleware.py`
- **Nhiệm vụ:** Tạo mã định duy nhất cho mỗi yêu cầu để truy vết trên toàn bộ hệ thống.
- **Kết quả:** 
  - Đã triển khai `CorrelationIdMiddleware` để tự động sinh `x-request-id` dưới dạng `req-xxxxxxxx`.
  - Sử dụng `bind_contextvars` của Structlog để gắn mã này vào mọi dòng log liên quan đến request đó.
  - Mã này cũng được trả về trong Header của phản hồi để Client dễ dàng đối soát.

### 1.2. Làm giàu dữ liệu Log (Log Enrichment)
- **Tập tin:** `app/main.py`
- **Nhiệm vụ:** Đưa các thông tin ngữ cảnh quan trọng vào log để phục vụ phân tích.
- **Kết quả:** 
  - Tại endpoint `/chat`, đã triển khai băm (hashing) `user_id` để bảo mật.
  - Gắn thêm các trường `session_id`, `feature`, `model`, và `env` vào context của log cho mọi hành động của người dùng.

### 1.3. Hệ thống Hủy dữ liệu nhạy cảm (PII Scrubbing & Redaction)
- **Tập tin:** `app/pii.py`, `app/logging_config.py`
- **Nhiệm vụ:** Ngăn chặn việc ghi lại thông tin cá nhân của người dùng vào log file.
- **Kết quả:**
  - Định nghĩa các Regular Expressions trong `app/pii.py` để nhận diện: Số hộ chiếu (Passport), Số điện thoại Việt Nam, Địa chỉ, và thẻ tín dụng.
  - Đăng ký bộ vi xử lý `scrub_event` vào pipeline của Structlog tại `app/logging_config.py`.
  - Mọi dữ liệu khớp mẫu sẽ tự động được thay thế bằng chuỗi `[REDACTED_...]`.

---

## 2. Đóng góp hỗ trợ Team (Member B - Tracing)

Mặc dù phụ trách Member A, tôi đã chủ động hỗ trợ Member B hoàn thiện hệ thống Tracing bằng cách:
- **Xử lý xung đột phiên bản:** Hạ cấp thư viện `langfuse` từ 3.x xuống 2.x để tương phục với mã nguồn mẫu của Lab (do 3.x thay đổi cách import decorators).
- **Đồng bộ ID:** Sửa lỗi logic tại `app/agent.py` để truyền mã `correlation_id` (từ Member A) vào Metadata của Langfuse Trace, giúp kết nối Logs và Traces làm một.
- **Gỡ lỗi 500:** Khắc phục lỗi TypeError khi gọi `update_current_trace` sai tham số.
- **Đảm bảo dữ liệu:** Thêm sự kiện `shutdown` để `flush` dữ liệu lên Langfuse Cloud ngay lập tức khi tắt server.

---

## 3. Xác minh kết quả
- Hoàn thành 100% các khối `TODO` được giao.
- Chạy script `scripts/validate_logs.py` đạt điểm tuyệt đối: **100/100**.
- Traces và Logs đã hiển thị đầy đủ, đồng bộ trên Langfuse Cloud.
