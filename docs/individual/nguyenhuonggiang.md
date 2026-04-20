# Bao cao ca nhan - Nguyen Thi Huong Giang (Member B)

## 1. Vai tro duoc phan cong
- Ho ten: Nguyen Thi Huong Giang
- Vai tro: Member B - Tracing va Enrichment
- Muc tieu: Dam bao request duoc trace day du tren Langfuse, co trace ID/correlation ID de debug theo luong Metrics -> Traces -> Logs.

## 2. Nhiem vu da hoan thanh
- Cai dat Langfuse skill tu `github.com/langfuse/skills` vao thu muc `.skills/langfuse` de tham chieu best practices khi instrument.
- Refactor helper tracing de tranh roi vao no-op fallback khi import sai API Langfuse.
- Chuan hoa tracing context:
- Tao trace id co tinh tai lap tu request id (`create_trace_id(seed=request_id)`).
- Dat ten root span theo feature (`chat-qa`, `chat-summary`) de de loc trong Langfuse.
- Bo sung metadata de enrich trace (user/session/feature/model/request_id).
- Instrument cac observation con:
- `Retrieve_Context` ghi input/output an toan.
- `LLM_Generate` ghi model, usage tokens, answer preview.
- Sua middleware de request nao cung co `x-request-id`, bind `request_id`/`correlation_id` vao contextvars.  
- Xu ly loi 401 Unauthorized khi export spans:
- Xac dinh nguyen nhan la moi truong chi co `LANGFUSE_BASE_URL` ma thieu `LANGFUSE_HOST`.
- Bo sung map `LANGFUSE_BASE_URL -> LANGFUSE_HOST` trong code va cap nhat `.env`.

## 3. Bang chung ky thuat (Code)
- File tracing trung tam: `app/tracing.py`
- Middleware correlation/request ID: `app/middleware.py`
- Bind context cho request: `app/main.py`
- Root span va trace attributes: `app/agent.py`
- Generation observation: `app/mock_llm.py`
- Retrieval observation: `app/mock_rag.py`
- Cau hinh host moi truong Langfuse: `.env`

## 4. Bang chung van hanh (Run-time)
- Sau khi fix, load test tra ve request id dung dinh dang:
- Mau output: `[200] req-e6cdbbac | qa | ...ms`
- Khong con trang thai `MISSING` trong request logs moi.
- Kiem tra log gan nhat:
- `recent_records: 20`
- `missing_id_records: 0`
- Kiem tra API Langfuse bang `.venv`:
- `trace_api_ok: 3`
- Mau trace IDs:
- `ad6ac639084b75d88de913273441f12d`
- `e45ea278e27d4d644ecbdcd6a0235968`
- `8b66cbd35d43e4d4fe361c4de510425c`
- Mau trace names:
- `chat-qa`, `chat-summary`

## 5. Root cause va cach khac phuc
- Van de 1: Log co `correlation_id`/`request_id = MISSING`.
- Nguyen nhan: `app/middleware.py` bi revert ve TODO, khong generate va khong bind contextvars.
- Khac phuc: Khoi phuc generate `req-<8-hex>`, bind contextvars, va add response headers.

- Van de 2: `Failed to export span batch code: 401 Unauthorized`.
- Nguyen nhan: Cac credentials hop le nhung `get_client()` trong setup hien tai can `LANGFUSE_HOST`; bien nay bi thieu.
- Khac phuc: Them `LANGFUSE_HOST` vao `.env` va normalize tu `LANGFUSE_BASE_URL` trong `app/tracing.py`.

## 6. Tu danh gia theo rubric cho phan Member B
- Hoan thanh vai tro Tracing & Enrichment:
- Co trace live tren Langfuse.
- Co metadata can thiet (feature/model/session/user hash/request_id).
- Co trace naming ro rang va span hierarchy de phuc vu debug.
- Da xu ly duoc loi runtime nghiem trong (401 export) de dam bao demo on dinh.

## 7. De xuat cai tien tiep theo
- Chot mot script smoke test tu dong:
- Ping `/health`
- Gui 10 request `/chat`
- Check Langfuse trace count >= 10 truoc demo
- Day nhanh ve SDK pattern moi (v4 migration) khi mon hoc yeu cau nang cap de giam technical debt.

## 8. Ket luan
Phan viec Member B da dat muc tieu: tracing hoat dong on dinh, co du context de debug incident, va da xu ly dut diem loi `MISSING correlation/request id` cung nhu loi `401 Unauthorized` khi export spans.
