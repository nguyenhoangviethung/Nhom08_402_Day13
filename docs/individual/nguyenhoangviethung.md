# Bao cao ca nhan - Nguyen Hoang Viet Hung (Member F)

## 1. Vai tro duoc phan cong
- Ho ten: Nguyen Hoang Viet Hung
- Vai tro: Member F - Blueprint owner, Demo lead, va code reviewer toan nhom
- Muc tieu:
  - Chot chat luong ky thuat truoc demo.
  - Dam bao handover ro rang neu Member D/E con backlog.
  - Review toan bo codebase de giam rui ro runtime trong live demo.

## 2. Nhiem vu da hoan thanh

### 2.1 Nhan nhiem vu dieu phoi va gate tong
- Nang cap gate pre-demo de kiem tra dong bo A/B/C/D/E truoc khi nop.
- Gate tu dong phat hien backlog D/E va in action handover sang Member F.
- Cac cap nhat chinh:
  - scripts/member_f_gate.py
  - docs/blueprint-template.md
  - guide.md

### 2.2 Nang cap phan viec Member D (Load Test + Incident Injection)
- Tao bo validator rieng cho Member D de kiem tra static + runtime.
- Xac nhan duoc 3 hanh vi incident can co:
  - rag_slow tang latency
  - tool_fail tra loi loi khi bat va recover sau khi tat
  - cost_spike tang chi phi so voi baseline
- Cac cap nhat chinh:
  - scripts/validate_member_d.py
  - guide.md
  - README.md

### 2.3 Nang cap phan viec Member E (Dashboard + Evidence)
- Tao bo validator rieng cho Member E de kiem tra:
  - dashboard 6 panels
  - unit/threshold
  - map metric key runtime
  - do day du evidence screenshot
- Chuan hoa dashboard spec de dong bo voi SLO runtime cua Member C.
- Chuan hoa evidence checklist theo owner/fallback, bo sung quy tac D/E -> F.
- Cac cap nhat chinh:
  - scripts/validate_member_e.py
  - docs/dashboard-spec.md
  - docs/grading-evidence.md
  - guide.md
  - README.md

### 2.4 Dong bo lien member (A/B/C/D/E/F)
- Dong bo role va deliverables trong report template de tranh lech scope.
- Dong bo command trong README va guide de team chay cung 1 quy trinh truoc demo.
- Dam bao cac script validator co the dung chung trong gate cua Member F.

## 3. Tong hop nang cap theo tung member
- Member A:
  - Duy tri quality gate phan logs/PII trong gate tong (log score + pii hits + correlation).
- Member B:
  - Ho tro spam traffic va xac minh trace live tren Langfuse de bo sung evidence.
- Member C:
  - Dong bo dashboard threshold voi SLO (`latency_p95_ms <= 3000ms`) de tranh xung dot tai lieu.
- Member D:
  - Bo sung validator runtime day du cho incident behavior.
- Member E:
  - Bo sung validator evidence/dashboard va danh sach backlog can handover.
- Member F:
  - Tich hop D/E checks vao gate tong va quy trinh takeover trong docs.

## 4. Ket qua kiem tra gan nhat
- Member D validator:
  - PASS (`python scripts/validate_member_d.py --check-runtime --strict`)
- Member E validator:
  - FAIL o evidence completeness (thieu anh trace list, trace waterfall, dashboard 6 panels, alert rules)
- Member F gate:
  - Tu dong phat action handover backlog Member E cho Member F.

## 5. Nhiem vu con lai cua toi (Member F)
- Review toan bo codebase truoc khi khoa ban nop (nhiem vu chinh con lai).
- Chot report template va xoa toan bo placeholder chua dien.
- Hoan tat evidence thieu (neu owner chua cap nhat kip, Member F tiep quan theo co che handover).
- Chay gate cuoi:
  - python scripts/member_f_gate.py --check-member-de-runtime --strict

## 6. Cam ket trach nhiem
Toi xac nhan da thuc hien vai tro Member F o muc dieu phoi, nang cap lien-member, va thiet lap co che handover ro rang. Phan viec con lai cua toi la review toan bo code va chot bo evidence/report de dam bao demo va nop bai an toan.
