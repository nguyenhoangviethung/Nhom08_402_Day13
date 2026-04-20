# Bao cao ca nhan - Day 13 Observability Lab

## 1. Thong tin ca nhan
- Ho ten: Le Hong Anh
- Role: Member C - SLO + Alerts
- Nhom: Nhom08_402_Day13

## 2. Muc tieu phan cong
Phu trach thiet ke, trien khai va kiem thu he thong SLO + Alerts cho ung dung lab:
- Dinh nghia va danh gia SLO tu metrics runtime.
- Danh gia trang thai alert firing theo alert rules.
- Mo endpoint de demo live trong buoi cham.
- Bo sung test de chung minh logic dung.

## 3. Cong viec da thuc hien
### 3.1 Trien khai logic danh gia SLO
- Tao module `app/slo_alerts.py` de:
  - Doc cau hinh tu `config/slo.yaml`.
  - Mapping SLI sang metric runtime (`latency_p95`, `error_rate_pct`, `daily_cost_usd`, `quality_avg`).
  - Danh gia pass/fail theo objective tung SLI.
  - Tong hop `overall_status` cho toan bo service.

### 3.2 Trien khai logic danh gia Alerts
- Trong `app/slo_alerts.py`:
  - Doc cau hinh tu `config/alert_rules.yaml`.
  - Parse va danh gia condition dang:
    - Absolute threshold: `metric > value for Xm`.
    - Baseline factor: `hourly_cost_usd > 2x_baseline for Xm`.
  - Tra ket qua cho tung alert: `ok` hoac `firing` + evidence de giai thich root cause.

### 3.3 Mo endpoint cho demo va giam sat
- Cap nhat `app/main.py`:
  - Them GET `/slo` de xem trang thai SLO hien tai.
  - Them GET `/alerts` de xem trang thai alert hien tai.

### 3.4 Mo rong metrics phuc vu alerting
- Cap nhat `app/metrics.py`:
  - Them `total_errors`, `error_rate_pct`.
  - Them `hourly_cost_usd`, `daily_cost_usd`.
  - Dam bao du lieu du cho SLO va alert conditions.

### 3.5 Bo sung unit tests
- Tao `tests/test_slo_alerts.py`:
  - Test SLO pass case.
  - Test SLO fail case.
  - Test alert firing cho latency/error.
  - Test alert firing cho cost spike.


## 4. Ket qua va evidence ky thuat
- Unit test da pass:
  - Lenh chay: `PYTHONPATH=. /home/anhle/vinuni/week_04/Nhom08_402_Day13/.venv/bin/pytest -q`
  - Ket qua: `6 passed`.
- Load test da chay thanh cong:
  - Lenh chay: `python scripts/load_test.py --concurrency 5`
  - Ket qua: exit code 0.

## 5. Cach demo phan viec Member C
1. Chay app: `uvicorn app.main:app --reload`
2. Kiem tra baseline:
   - `curl -s http://127.0.0.1:8000/slo`
   - `curl -s http://127.0.0.1:8000/alerts`
3. Bat incident theo scenario:
   - `python scripts/inject_incident.py --scenario rag_slow`
   - `python scripts/inject_incident.py --scenario tool_fail`
   - `python scripts/inject_incident.py --scenario cost_spike`
4. Baan traffic:
   - `python scripts/load_test.py --concurrency 5`
5. Kiem tra alert firing va doi chieu runbook trong `docs/alerts.md`.

## 6. Tu danh gia dong gop
- Hoan thanh day du pham vi role Member C (SLO + Alerts).
- Co thay doi code runtime, endpoint API, va unit tests.
- Co command demo va evidence phu hop rubric cham diem.
