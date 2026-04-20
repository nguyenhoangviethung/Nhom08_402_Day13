# Báo cáo cá nhân - Day 13 Observability Lab

## 1. Thông tin cá nhân
- Họ tên: Lê Hồng Anh
- Role: Member C - SLO + Alerts
- Nhóm: Nhom08_402_Day13

## 2. Mục tiêu phân công
Phụ trách thiết kế, triển khai và kiểm thử hệ thống SLO + Alerts cho ứng dụng lab:
- Định nghĩa và đánh giá SLO từ metrics runtime.
- Đánh giá trạng thái alert firing theo alert rules.
- Mở endpoint để demo live trong buổi chấm.
- Bổ sung test để chứng minh logic đúng.

## 3. Công việc đã thực hiện
### 3.1 Triển khai logic đánh giá SLO
- Tạo module `app/slo_alerts.py` để:
  - Đọc cấu hình từ `config/slo.yaml`.
  - Mapping SLI sang metric runtime (`latency_p95`, `error_rate_pct`, `daily_cost_usd`, `quality_avg`).
  - Đánh giá pass/fail theo objective từng SLI.
  - Tổng hợp `overall_status` cho toàn bộ service.

### 3.2 Triển khai logic đánh giá Alerts
- Trong `app/slo_alerts.py`:
  - Đọc cấu hình từ `config/alert_rules.yaml`.
  - Parse và đánh giá condition dạng:
    - Absolute threshold: `metric > value for Xm`.
    - Baseline factor: `hourly_cost_usd > 2x_baseline for Xm`.
  - Trả kết quả cho từng alert: `ok` hoặc `firing` + evidence để giải thích root cause.

### 3.3 Mở endpoint cho demo và giám sát
- Cập nhật `app/main.py`:
  - Thêm GET `/slo` để xem trạng thái SLO hiện tại.
  - Thêm GET `/alerts` để xem trạng thái alert hiện tại.

### 3.4 Mở rộng metrics phục vụ alerting
- Cập nhật `app/metrics.py`:
  - Thêm `total_errors`, `error_rate_pct`.
  - Thêm `hourly_cost_usd`, `daily_cost_usd`.
  - Đảm bảo dữ liệu đủ cho SLO và alert conditions.

### 3.5 Bổ sung unit tests
- Tạo `tests/test_slo_alerts.py`:
  - Test SLO pass case.
  - Test SLO fail case.
  - Test alert firing cho latency/error.
  - Test alert firing cho cost spike.


## 4. Kết quả và evidence kỹ thuật
- Unit test đã pass:
  - Lệnh chạy: `PYTHONPATH=. /home/anhle/vinuni/week_04/Nhom08_402_Day13/.venv/bin/pytest -q`
  - Kết quả: `6 passed`.
- Load test đã chạy thành công:
  - Lệnh chạy: `python scripts/load_test.py --concurrency 5`
  - Kết quả: exit code 0.

## 5. Cách demo phần việc Member C
1. Chạy app: `uvicorn app.main:app --reload`
2. Kiểm tra baseline:
   - `curl -s http://127.0.0.1:8000/slo`
   - `curl -s http://127.0.0.1:8000/alerts`
3. Bật incident theo scenario:
   - `python scripts/inject_incident.py --scenario rag_slow`
   - `python scripts/inject_incident.py --scenario tool_fail`
   - `python scripts/inject_incident.py --scenario cost_spike`
4. Bắn traffic:
   - `python scripts/load_test.py --concurrency 5`
5. Kiểm tra alert firing và đối chiếu runbook trong `docs/alerts.md`.

## 6. Tự đánh giá đóng góp
- Hoàn thành đầy đủ phạm vi role Member C (SLO + Alerts).
- Có thay đổi code runtime, endpoint API, và unit tests.
- Có command demo và evidence phù hợp rubric chấm điểm.
