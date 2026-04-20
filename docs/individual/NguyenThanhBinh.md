# Báo cáo đóng góp cá nhân - Member E

**Họ và tên:** Nguyễn Thanh Bình
**Vai trò:** Giám sát chất lượng (QA), Dashboard & Thu thập bằng chứng.

## 1. Kết quả thực thi kỹ thuật (Validation)
- **Công việc:** Trực tiếp vận hành script `validate_logs.py` để kiểm soát chất lượng đầu ra của toàn nhóm.
- **Kết quả:** Xác nhận hệ thống đạt **100/100 điểm** kỹ thuật.
    - [x] **JSON Schema**: Cấu trúc log chuẩn chỉnh, hỗ trợ phân tích tự động.
    - [x] **Correlation ID**: Đảm bảo 100% request có định danh duy nhất để truy vết.
    - [x] **PII Scrubbing**: Bảo mật tuyệt đối thông tin nhạy cảm (Email, Phone) trong log.

## 2. Xây dựng Dashboard & Chỉ số (Metrics)
Đã định nghĩa và kiểm chứng bộ 6 chỉ số (Panels) cốt lõi cho hệ thống:
1. **Latency (P95)**: Theo dõi độ trễ để đảm bảo SLO < 500ms.
2. **Traffic**: Thống kê lưu lượng (Xác nhận 43+ request thực tế).
3. **Error Rate**: Giám sát tỉ lệ lỗi HTTP 4xx/5xx.
4. **AI Cost**: Theo dõi chi phí API theo thời gian thực (trường `cost_usd`).
5. **Token Usage**: Quản lý tài nguyên đầu vào/đầu ra (In/Out tokens).
6. **Security Proxy**: Giám sát trạng thái hoạt động của bộ lọc PII.

## 3. Phân tích sự cố (Incident Response)
- **Kịch bản:** Giả lập sự cố `rag_slow` (truy xuất dữ liệu chậm).
- **Phát hiện:** Qua giám sát log, đã nhận diện `latency_ms` tăng đột biến từ 150ms lên mức vi phạm ngưỡng an toàn.
- **Bằng chứng:** Đã thu thập Trace ID từ Member B để đối chiếu lỗi trên hệ thống Tracing của Langfuse.
