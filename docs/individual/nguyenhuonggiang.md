# Báo cáo cá nhân - Nguyễn Thị Hương Giang (Member B)

## 1. Vai trò được phân công
- Họ tên: Nguyễn Thị Hương Giang
- Vai trò: Member B - Tracing và Enrichment
- Mục tiêu: Đảm bảo request được trace đầy đủ trên Langfuse, có trace ID/correlation ID để debug theo luồng Metrics -> Traces -> Logs.

## 2. Nhiệm vụ đã hoàn thành
- Cài đặt Langfuse skill từ `github.com/langfuse/skills` vào thư mục `.skills/langfuse` để tham chiếu best practices khi instrument.
- Refactor helper tracing để tránh rơi vào no-op fallback khi import sai API Langfuse.
- Chuẩn hóa tracing context:
- Tạo trace id có tính tái lập từ request id (`create_trace_id(seed=request_id)`).
- Đặt tên root span theo feature (`chat-qa`, `chat-summary`) để dễ lọc trong Langfuse.
- Bổ sung metadata để enrich trace (user/session/feature/model/request_id).
- Instrument các observation con:
- `Retrieve_Context` ghi input/output an toàn.
- `LLM_Generate` ghi model, usage tokens, answer preview.
- Sửa middleware để request nào cũng có `x-request-id`, bind `request_id`/`correlation_id` vào contextvars.  
- Xử lý lỗi 401 Unauthorized khi export spans:
- Xác định nguyên nhân là môi trường chỉ có `LANGFUSE_BASE_URL` mà thiếu `LANGFUSE_HOST`.
- Bổ sung map `LANGFUSE_BASE_URL -> LANGFUSE_HOST` trong code và cập nhật `.env`.

## 3. Bằng chứng kỹ thuật (Code)
- File tracing trung tâm: `app/tracing.py`
- Middleware correlation/request ID: `app/middleware.py`
- Bind context cho request: `app/main.py`
- Root span và trace attributes: `app/agent.py`
- Generation observation: `app/mock_llm.py`
- Retrieval observation: `app/mock_rag.py`
- Cấu hình host môi trường Langfuse: `.env`

## 4. Bằng chứng vận hành (Run-time)
- Sau khi fix, load test trả về request id đúng định dạng:
- Mẫu output: `[200] req-e6cdbbac | qa | ...ms`
- Không còn trạng thái `MISSING` trong request logs mới.
- Kiểm tra log gần nhất:
- `recent_records: 20`
- `missing_id_records: 0`
- Kiểm tra API Langfuse bằng `.venv`:
- `trace_api_ok: 3`
- Mẫu trace IDs:
- `ad6ac639084b75d88de913273441f12d`
- `e45ea278e27d4d644ecbdcd6a0235968`
- `8b66cbd35d43e4d4fe361c4de510425c`
- Mẫu trace names:
- `chat-qa`, `chat-summary`

## 5. Root cause và cách khắc phục
- Vấn đề 1: Log có `correlation_id`/`request_id = MISSING`.
- Nguyên nhân: `app/middleware.py` bị revert về TODO, không generate và không bind contextvars.
- Khắc phục: Khôi phục generate `req-<8-hex>`, bind contextvars, và add response headers.

- Vấn đề 2: `Failed to export span batch code: 401 Unauthorized`.
- Nguyên nhân: Các credentials hợp lệ nhưng `get_client()` trong setup hiện tại cần `LANGFUSE_HOST`; biến này bị thiếu.
- Khắc phục: Thêm `LANGFUSE_HOST` vào `.env` và normalize từ `LANGFUSE_BASE_URL` trong `app/tracing.py`.

## 6. Tự đánh giá theo rubric cho phần Member B
- Hoàn thành vai trò Tracing & Enrichment:
- Có trace live trên Langfuse.
- Có metadata cần thiết (feature/model/session/user hash/request_id).
- Có trace naming rõ ràng và span hierarchy để phục vụ debug.
- Đã xử lý được lỗi runtime nghiêm trọng (401 export) để đảm bảo demo ổn định.

## 7. Đề xuất cải tiến tiếp theo
- Chốt một script smoke test tự động:
- Ping `/health`
- Gửi 10 request `/chat`
- Check Langfuse trace count >= 10 trước demo
- Đẩy nhanh về SDK pattern mới (v4 migration) khi môn học yêu cầu nâng cấp để giảm technical debt.

## 8. Kết luận
Phần việc Member B đã đạt mục tiêu: tracing hoạt động ổn định, có đủ context để debug incident, và đã xử lý dứt điểm lỗi `MISSING correlation/request id` cũng như lỗi `401 Unauthorized` khi export spans.
