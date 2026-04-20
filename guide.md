# Guide kiểm tra Member A và Member B

Tài liệu này dùng để kiểm tra nhanh phần việc của Member A và Member B theo rubric Day 13 Observability Lab.

## 1. Member A - Logging + PII

Mục tiêu cần đạt:
- Log JSON đúng schema.
- Có correlation ID xuyên suốt.
- Có enrichment cho API log: `user_id_hash`, `session_id`, `feature`, `model`.
- Không lộ PII trong log.

### File cần kiểm tra
- `app/middleware.py`
- `app/logging_config.py`
- `app/pii.py`
- `app/main.py`

### Checklist nhanh
1. Middleware có tạo `x-request-id` và bind vào context.
2. `app/main.py` bind được `request_id`, `correlation_id`, `trace_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`.
3. `app/logging_config.py` có processor chặn PII trước khi ghi log.
4. `app/pii.py` có regex scrub cho email, phone, CCCD, thẻ, passport, địa chỉ.
5. Log mới không còn ký tự email hoặc số thẻ test.

### Cách kiểm tra

```bash
python scripts/validate_logs.py
```

Kỳ vọng:
- `missing_required = 0`
- `missing_enrichment = 0`
- `Potential PII leaks detected = 0`
- `Estimated Score = 100/100`

### Cách kiểm tra thủ công log mới

```bash
tail -n 5 data/logs.jsonl
```

Một log API tốt nên có các field:
- `ts`
- `level`
- `service`
- `event`
- `correlation_id`
- `user_id_hash`
- `session_id`
- `feature`
- `model`

### Dấu hiệu Member A đạt
- `scripts/validate_logs.py` ra 100/100.
- `data/logs.jsonl` không có `@` hay số thẻ test trong các log mới.
- Request mới luôn có `correlation_id` và context đầy đủ.

---

## 2. Member B - Tracing + Tags

Mục tiêu cần đạt:
- Có trace trên Langfuse.
- Có hierarchy rõ ràng: root span -> retrieve -> generation.
- Có tags và metadata cho trace.
- Có ít nhất 10 traces live trên Langfuse.

### File cần kiểm tra
- `app/tracing.py`
- `app/agent.py`
- `app/mock_llm.py`
- `app/mock_rag.py`
- `app/main.py`

### Checklist nhanh
1. `app/tracing.py` import Langfuse đúng SDK đang dùng.
2. `app/main.py` load `.env` sớm và shutdown tracing khi app dừng.
3. `app/agent.py` tạo root span cho request chat và gắn `user_id`, `session_id`, `tags`, `metadata`.
4. `app/mock_rag.py` tạo span cho retrieval.
5. `app/mock_llm.py` tạo generation observation, có `model` và `usage_details`.

### Cách tạo trace mới

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how about refund policy?",
    "user_id": "user123_abc",
    "feature": "chatbot_support",
    "session_id": "session123_abc"
  }'
```

### Cách kiểm tra trên Langfuse CLI

```bash
set -a
source .env
set +a
npx -y langfuse-cli api traces list --limit 20
```

Hoặc kiểm tra một trace cụ thể:

```bash
npx -y langfuse-cli api traces get <trace-id>
```

### Dấu hiệu Member B đạt
- Có trace tên `chat-response` hoặc `chat-<feature>` trên Langfuse.
- Trace có `tags`, `userId`, `sessionId`, `metadata`.
- Trace có 3 observation con: root span, retrieve span, generation span.
- Tổng số trace live >= 10.

---

## 3. Quy trình demo nhanh

1. Mở API health để chắc chắn tracing đang bật.
2. Gửi 1 request chat để tạo log và trace.
3. Chạy `scripts/validate_logs.py` để kiểm tra Member A.
4. Mở Langfuse Tracing để kiểm tra Member B.
5. Nếu UI chưa hiện trace, dùng CLI để xác nhận dữ liệu đã vào project.

```bash
curl -s http://127.0.0.1:8000/health
python scripts/validate_logs.py
npx -y langfuse-cli api traces list --limit 20
```

---

## 4. Kết luận chấm nhanh

- Member A đạt tốt khi: log sạch, đủ context, không PII, validator 100/100.
- Member B đạt tốt khi: trace lên cloud, đủ hierarchy, đủ tags/metadata, có tối thiểu 10 traces.

---

## 5. Plan thực thi cho Member F để đạt điểm tuyệt đối

Vai trò khuyến nghị cho Member F:
- Blueprint report owner (điền, kiểm, khóa bản nộp).
- Demo lead (điều phối phần trình bày và xử lý Q&A).
- Evidence curator (gom ảnh, link commit/PR, đối chiếu rubric).

Mục tiêu điểm:
- Chốt toàn bộ điều kiện đạt của Group Score.
- Tối đa điểm Individual: phần report cá nhân + bằng chứng Git rõ ràng.

### 5.1 Deliverables bắt buộc trước giờ demo

1. Report hoàn chỉnh theo mẫu:
- Điền đủ tag trong `docs/blueprint-template.md`.
- Không để sót placeholder kiểu `[GROUP_NAME]`, `[EVIDENCE_LINK]`, `[TRACE_WATERFALL_EXPLANATION]`.

2. Bộ evidence đầy đủ theo checklist:
- Dùng `docs/grading-evidence.md` làm nguồn kiểm.
- Bắt buộc có ảnh: trace list >= 10, trace waterfall, log correlation_id, log PII redaction, dashboard 6 panels, alert rules + runbook.

3. Chốt số liệu kỹ thuật cuối cùng:
- `VALIDATE_LOGS_FINAL_SCORE`.
- `TOTAL_TRACES_COUNT`.
- `PII_LEAKS_FOUND`.

4. Bằng chứng cá nhân từng thành viên:
- Mỗi member có ít nhất 1 commit/PR link trong mục Individual Contributions.

### 5.2 Timeline thực thi (khuyến nghị T-120 đến T-0)

T-120 đến T-90 (Freeze kỹ thuật):
1. Pull nhánh demo mới nhất.
2. Chạy kiểm tra nhanh:
  - `python scripts/validate_logs.py`
  - `curl -s http://127.0.0.1:8000/health`
  - `npx -y langfuse-cli api traces list --limit 20`
3. Nếu trace < 10, bơm thêm request trước khi chụp ảnh.

T-90 đến T-60 (Khóa evidence):
1. Chụp đủ ảnh theo `docs/grading-evidence.md`.
2. Đặt tên ảnh thống nhất (ví dụ: `evidence_trace_list.png`, `evidence_dashboard_6_panels.png`).
3. Điền đường dẫn ảnh vào `docs/blueprint-template.md`.

T-60 đến T-30 (Hoàn thiện report):
1. Viết ngắn gọn nhưng có bằng chứng cho Incident Response:
  - Symptoms
  - Root cause (trace id/log line cụ thể)
  - Fix action
  - Preventive measure
2. Điền đầy đủ phần cá nhân cho từng member + link commit/PR.

T-30 đến T-10 (Dry run):
1. Rehearsal 1 vòng đủ flow:
  - Health check -> request -> logs -> traces -> dashboard -> alerts -> incident RCA.
2. Canh thời gian tổng 8-10 phút.
3. Member F tập câu chuyển mạch giữa các phần, không để chết màn.

T-10 đến T-0 (Final gate):
1. Chạy lại 3 lệnh kiểm tra cốt lõi.
2. Verify không còn placeholder trong report.
3. Chốt người trả lời Q&A theo chủ đề.

Lệnh gate một phát cho Member F:

```bash
python scripts/member_f_gate.py --strict
```

### 5.3 Kịch bản demo gợi ý để ăn trọn điểm Live Demo

1. Mở đầu (30s): nêu mục tiêu observability và tiêu chí đạt.
2. Logging + PII (2 phút):
- Show log JSON có correlation_id và context.
- Show ví dụ dữ liệu nhạy cảm đã bị redact.
3. Tracing (2 phút):
- Show trace list (>=10).
- Mở 1 waterfall và giải thích root span -> retrieve -> generation.
4. Dashboard + SLO + Alerts (2 phút):
- Show đủ 6 panels có đơn vị và threshold line.
- Show 3 alert rule và runbook link.
5. Incident RCA (2 phút):
- Kể flow điều tra Metrics -> Traces -> Logs.
- Chỉ ra root cause bằng trace/log cụ thể.
6. Kết thúc (30s): nhắc pass criteria đã đạt.

### 5.4 Bộ câu trả lời Q&A cần chuẩn bị (Member F điều phối)

1. Correlation ID truyền xuyên suốt như thế nào và giúp gì khi debug?
2. Vì sao cần scrub PII ở cả payload và event text?
3. Vì sao trace cần tags và metadata (feature, session, user hash)?
4. Cách chứng minh root cause khi inject incident `rag_slow` hoặc `tool_fail`?
5. Nếu Langfuse UI không hiện trace nhưng CLI có dữ liệu thì xử lý ra sao?

### 5.5 Definition of Done cho Member F

Chỉ coi là xong khi đồng thời đạt:
1. Report `docs/blueprint-template.md` điền đủ 100%, không placeholder.
2. `python scripts/validate_logs.py` đạt >= 80 (mục tiêu 100).
3. Langfuse có >= 10 traces live.
4. Bộ ảnh evidence đủ theo `docs/grading-evidence.md`.
5. Mỗi member có link commit/PR trong phần cá nhân.
6. Đã rehearsal ít nhất 1 lần full flow 8-10 phút.
