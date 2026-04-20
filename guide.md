# Guide kiểm tra Member A, B, C, D và F

Tài liệu này dùng để kiểm tra nhanh phần việc của Member A, B, C, D và F theo rubric Day 13 Observability Lab.

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

## 3. Member C - SLO + Alerts

Mục tiêu cần đạt:
- Có cấu hình SLO hợp lệ và khớp metric runtime.
- Có ít nhất 3 alert rules, có runbook link hoạt động.
- Endpoint `/slo` và `/alerts` trả dữ liệu đúng cấu trúc.

### File cần kiểm tra
- `config/slo.yaml`
- `config/alert_rules.yaml`
- `docs/alerts.md`
- `app/slo_alerts.py`
- `app/main.py`

### Checklist nhanh
1. `config/slo.yaml` có đủ 4 SLI: `latency_p95_ms`, `error_rate_pct`, `daily_cost_usd`, `quality_score_avg`.
2. `config/alert_rules.yaml` có tối thiểu 3 alert: `high_latency_p95`, `high_error_rate`, `cost_budget_spike`.
3. Mỗi alert có đủ `severity`, `condition`, `owner`, `runbook`.
4. Runbook link trỏ đúng heading thật trong `docs/alerts.md`.
5. Endpoint `/slo` và `/alerts` trả về 200 và có keys bắt buộc.

### Cách kiểm tra tự động

```bash
python scripts/validate_member_c.py --check-runtime --strict
```

### Dấu hiệu Member C đạt tối đa
- Static config PASS (SLO + alerts + runbook anchors).
- Runtime endpoint PASS (`/metrics`, `/slo`, `/alerts`).
- Không còn placeholder dạng starter note trong SLO config.

---

## 4. Member D - Load Test + Incident Injection

Mục tiêu cần đạt:
- Có load test tạo traffic ổn định và xuất thống kê `throughput`, `latency p50/p95/p99`.
- Có incident injection cho đủ 3 kịch bản: `rag_slow`, `tool_fail`, `cost_spike`.
- Chứng minh được before/after khi bật incident bằng dữ liệu runtime thực tế.
- Tương thích luồng của A/B/C: request sinh ra log, trace, metrics dùng lại cho SLO/alerts.

### File cần kiểm tra
- `scripts/load_test.py`
- `scripts/inject_incident.py`
- `scripts/validate_member_d.py`
- `app/incidents.py`
- `app/mock_rag.py`
- `app/mock_llm.py`
- `data/incidents.json`

### Checklist nhanh
1. `load_test.py` có đủ tham số `--base-url`, `--query-file`, `--concurrency`, `--repeat`, `--timeout`, `--skip-metrics`.
2. `inject_incident.py` có `--list`, `--status`, `--scenario`, và toggle enable/disable qua API.
3. `/health` phản ánh đúng trạng thái 3 incident sau khi toggle.
4. Runtime behavior đúng kỳ vọng:
  - `rag_slow` làm tăng latency rõ rệt.
  - `tool_fail` gây lỗi 500 khi bật và recover sau khi tắt.
  - `cost_spike` làm tăng chi phí so với baseline.
5. Sau kiểm tra, toàn bộ incident phải trở về `False` để không ảnh hưởng Member C/F demo.

### Cách kiểm tra tự động

```bash
python scripts/validate_member_d.py --check-runtime --strict
```

### Cách kiểm tra thủ công nhanh

```bash
python scripts/inject_incident.py --status
python scripts/load_test.py --concurrency 5 --repeat 1
python scripts/inject_incident.py --scenario rag_slow
python scripts/load_test.py --concurrency 2 --repeat 1
python scripts/inject_incident.py --scenario rag_slow --disable
python scripts/inject_incident.py --status
```

### Dấu hiệu Member D đạt tối đa
- `scripts/validate_member_d.py --check-runtime --strict` PASS.
- Load test summary có đủ `throughput`, `latency avg`, `p50`, `p95`, `p99`.
- Demo được flow incident RCA theo chuỗi `Metrics -> Traces -> Logs` cho ít nhất 1 incident.
- Kết thúc bài test, incident state sạch (`rag_slow=false`, `tool_fail=false`, `cost_spike=false`).

---

## 5. Member E - Dashboard + Evidence

Mục tiêu cần đạt:
- Dashboard đủ 6 panels, có đơn vị đo và threshold/SLO line rõ ràng.
- Mapping panel khớp metric key runtime để không lệch với Member C.
- Bộ evidence bắt buộc có ảnh và link hợp lệ theo checklist.
- Nếu thiếu evidence, có danh sách handover rõ ràng cho Member F.

### File cần kiểm tra
- `docs/dashboard-spec.md`
- `docs/grading-evidence.md`
- `scripts/validate_member_e.py`
- `scripts/member_f_gate.py`
- `docs/blueprint-template.md`

### Checklist nhanh
1. Dashboard spec mô tả đủ 6 panel: latency, traffic, error rate, cost, tokens, quality/security.
2. Ngưỡng latency trong dashboard spec khớp `config/slo.yaml` (`latency_p95_ms <= 3000ms`).
3. Có ghi rõ đơn vị (`ms`, `USD`, `count`) và threshold line.
4. `docs/grading-evidence.md` có đủ item evidence bắt buộc.
5. Các ảnh evidence được link đúng path tồn tại trong repo.
6. Nếu item D/E chưa xong, phải có action chuyển cho Member F trong gate output.

### Cách kiểm tra tự động

```bash
python scripts/validate_member_e.py --check-runtime --strict
```

### Cách kiểm tra handover D/E -> F

```bash
python scripts/member_f_gate.py --check-member-de-runtime --strict
```

### Dấu hiệu Member E đạt tối đa
- `scripts/validate_member_e.py --check-runtime --strict` PASS.
- Dashboard spec đồng bộ SLO/metrics với Member C.
- Evidence sheet đủ ảnh bắt buộc và không có link hỏng.
- Gate tổng không phát sinh action handover từ D/E sang F.

---

## 6. Quy trình demo nhanh

1. Mở API health để chắc chắn tracing đang bật.
2. Gửi 1 request chat để tạo log và trace.
3. Chạy `scripts/validate_logs.py` để kiểm tra Member A.
4. Chạy `scripts/validate_member_d.py --check-runtime` để kiểm tra Member D.
5. Chạy `scripts/validate_member_e.py --check-runtime` để kiểm tra Member E.
6. Mở Langfuse Tracing để kiểm tra Member B.
7. Nếu UI chưa hiện trace, dùng CLI để xác nhận dữ liệu đã vào project.

```bash
curl -s http://127.0.0.1:8000/health
python scripts/validate_logs.py
python scripts/validate_member_d.py --check-runtime
python scripts/validate_member_e.py --check-runtime
npx -y langfuse-cli api traces list --limit 20
```

---

## 7. Kết luận chấm nhanh

- Member A đạt tốt khi: log sạch, đủ context, không PII, validator 100/100.
- Member B đạt tốt khi: trace lên cloud, đủ hierarchy, đủ tags/metadata, có tối thiểu 10 traces.
- Member C đạt tốt khi: SLO/alert đúng chuẩn, runbook hoạt động, endpoint `/slo` và `/alerts` kiểm chứng được.
- Member D đạt tốt khi: load test có số liệu đủ sâu, incident toggle đúng hành vi và chứng minh được before/after khi debug.
- Member E đạt tốt khi: dashboard đồng bộ metric/SLO, evidence đủ và sẵn sàng đóng gói cho report.

---

## 8. Plan thực thi cho Member F để đạt điểm tuyệt đối

Vai trò khuyến nghị cho Member F:
- Blueprint report owner (điền, kiểm, khóa bản nộp).
- Demo lead (điều phối phần trình bày và xử lý Q&A).
- Evidence curator (gom ảnh, link commit/PR, đối chiếu rubric).

Mục tiêu điểm:
- Chốt toàn bộ điều kiện đạt của Group Score.
- Tối đa điểm Individual: phần report cá nhân + bằng chứng Git rõ ràng.

### 8.1 Deliverables bắt buộc trước giờ demo

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

### 8.2 Timeline thực thi (khuyến nghị T-120 đến T-0)

T-120 đến T-90 (Freeze kỹ thuật):
1. Pull nhánh demo mới nhất.
2. Chạy kiểm tra nhanh:
  - `python scripts/validate_logs.py`
  - `python scripts/validate_member_d.py --check-runtime`
  - `python scripts/validate_member_e.py --check-runtime`
  - `curl -s http://127.0.0.1:8000/health`
  - `npx -y langfuse-cli api traces list --limit 20`
3. Nếu trace < 10, bơm thêm request trước khi chụp ảnh.
4. Nếu `validate_member_d/e` FAIL, Member F nhận takeover backlog và ghi rõ trong phần cá nhân của Member F.

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
4. Nếu gate báo thiếu D/E, Member F xác nhận ownership và cập nhật evidence ngay trước demo.

Lệnh gate một phát cho Member F:

```bash
python scripts/member_f_gate.py --check-member-de-runtime --strict
```

Auto điền 3 chỉ số nhóm vào report:

```bash
python scripts/member_f_gate.py --write-group-metrics
```

### 8.3 Kịch bản demo gợi ý để ăn trọn điểm Live Demo

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

### 8.4 Bộ câu trả lời Q&A cần chuẩn bị (Member F điều phối)

1. Correlation ID truyền xuyên suốt như thế nào và giúp gì khi debug?
2. Vì sao cần scrub PII ở cả payload và event text?
3. Vì sao trace cần tags và metadata (feature, session, user hash)?
4. Cách chứng minh root cause khi inject incident `rag_slow` hoặc `tool_fail`?
5. Nếu Langfuse UI không hiện trace nhưng CLI có dữ liệu thì xử lý ra sao?

### 8.5 Definition of Done cho Member F

Chỉ coi là xong khi đồng thời đạt:
1. Report `docs/blueprint-template.md` điền đủ 100%, không placeholder.
2. `python scripts/validate_logs.py` đạt >= 80 (mục tiêu 100).
3. Langfuse có >= 10 traces live.
4. Bộ ảnh evidence đủ theo `docs/grading-evidence.md`.
5. Mỗi member có link commit/PR trong phần cá nhân.
6. Đã rehearsal ít nhất 1 lần full flow 8-10 phút.
7. Nếu D/E có backlog, đã ghi takeover của Member F trong report và có bằng chứng kèm theo.
