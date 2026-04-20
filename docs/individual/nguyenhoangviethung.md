# Báo cáo cá nhân - Nguyễn Hoàng Việt Hùng (Member F)

## 1. Vai trò được phân công
- Họ tên: Nguyễn Hoàng Việt Hùng
- Vai trò: Member F - Blueprint owner, Demo lead, và code reviewer toàn nhóm
- Mục tiêu:
  - Chốt chất lượng kỹ thuật trước demo.
  - Đảm bảo handover rõ ràng nếu Member D/E còn backlog.
  - Review toàn bộ codebase để giảm rủi ro runtime trong live demo.

## 2. Nhiệm vụ đã hoàn thành

### 2.1 Nhận nhiệm vụ điều phối và gate tổng
- Nâng cấp gate pre-demo để kiểm tra đồng bộ A/B/C/D/E trước khi nộp.
- Gate tự động phát hiện backlog D/E và in action handover sang Member F.
- Các cập nhật chính:
  - scripts/member_f_gate.py
  - docs/blueprint-template.md
  - guide.md

### 2.2 Nâng cấp phần việc Member D (Load Test + Incident Injection)
- Tạo bộ validator riêng cho Member D để kiểm tra static + runtime.
- Xác nhận được 3 hành vi incident cần có:
  - rag_slow tăng latency
  - tool_fail trả lỗi khi bật và recover sau khi tắt
  - cost_spike tăng chi phí so với baseline
- Các cập nhật chính:
  - scripts/validate_member_d.py
  - guide.md
  - README.md

### 2.3 Nâng cấp phần việc Member E (Dashboard + Evidence)
- Tạo bộ validator riêng cho Member E để kiểm tra:
  - dashboard 6 panels
  - unit/threshold
  - map metric key runtime
  - độ đầy đủ evidence screenshot
- Chuẩn hóa dashboard spec để đồng bộ với SLO runtime của Member C.
- Chuẩn hóa evidence checklist theo owner/fallback, bổ sung quy tắc D/E -> F.
- Các cập nhật chính:
  - scripts/validate_member_e.py
  - docs/dashboard-spec.md
  - docs/grading-evidence.md
  - guide.md
  - README.md

### 2.4 Đồng bộ liên member (A/B/C/D/E/F)
- Đồng bộ role và deliverables trong report template để tránh lệch scope.
- Đồng bộ command trong README và guide để team chạy cùng 1 quy trình trước demo.
- Đảm bảo các script validator có thể dùng chung trong gate của Member F.

## 3. Tổng hợp nâng cấp theo từng member
- Member A:
  - Duy trì quality gate phần logs/PII trong gate tổng (log score + pii hits + correlation).
- Member B:
  - Hỗ trợ spam traffic và xác minh trace live trên Langfuse để bổ sung evidence.
- Member C:
  - Đồng bộ dashboard threshold với SLO (`latency_p95_ms <= 3000ms`) để tránh xung đột tài liệu.
- Member D:
  - Bổ sung validator runtime đầy đủ cho incident behavior.
- Member E:
  - Bổ sung validator evidence/dashboard và danh sách backlog cần handover.
- Member F:
  - Tích hợp D/E checks vào gate tổng và quy trình takeover trong docs.

## 4. Kết quả kiểm tra gần nhất
- Member D validator:
  - PASS (`python scripts/validate_member_d.py --check-runtime --strict`)
- Member E validator:
  - FAIL ở evidence completeness (thiếu ảnh trace list, trace waterfall, dashboard 6 panels, alert rules)
- Member F gate:
  - Tự động phát action handover backlog Member E cho Member F.

## 5. Nhiệm vụ còn lại của tôi (Member F)
- Review toàn bộ codebase trước khi khóa bản nộp (nhiệm vụ chính còn lại).
- Chốt report template và xóa toàn bộ placeholder chưa điền.
- Hoàn tất evidence thiếu (nếu owner chưa cập nhật kịp, Member F tiếp quản theo cơ chế handover).
- Chạy gate cuối:
  - python scripts/member_f_gate.py --check-member-de-runtime --strict

## 6. Cam kết trách nhiệm
Tôi xác nhận đã thực hiện vai trò Member F ở mức điều phối, nâng cấp liên-member, và thiết lập cơ chế handover rõ ràng. Phần việc còn lại của tôi là review toàn bộ code và chốt bộ evidence/report để đảm bảo demo và nộp bài an toàn.
