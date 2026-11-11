# Estimate backlog LAB-5 — Sakura Market

> Báo cáo SWP (HTML, chỉ đọc): [`reports/estimate-swp-sakura-market-lab5-20261111.html`](reports/estimate-swp-sakura-market-lab5-20261111.html)
>
> **Tóm tắt:** 273 issue lá · **1,247 SWP** · **2,122 giờ** · calibration `accepted` (5 issue mẫu giữ nguyên, 0 issue đổi điểm).

Phạm vi: 12 epic E00〜E11, 324 issue dev (12 epic + 39 issue cha + 273 issue lá). Số liệu lấy từ `backlog-data/`, `generated/swp-by-key.json`, `generated/hours-vs-swp.json`, `generated/report-tables.md`. Giờ của issue cha = tổng giờ các lá, không tính riêng.

---

## 1. Issue mẫu skill chọn để kiểm (calibration)

Skill `estimate-swp` (level medium, mô hình `swp-matrix-v2`) tự chấm 273 lá, rồi chọn 5 issue đại diện cho các điểm khác nhau trên thang để người dùng kiểm. Body gửi worker đã bỏ dòng giờ ước lượng, nên điểm SWP không bị giờ có sẵn kéo theo.

| Issue | Lý do skill chọn | Skill chấm (Scope × Complexity → SWP) | Bạn chốt | Lý do giữ |
|---|---|---|---|---|
| #74 (E02-04b) Dialog 一時停止 trên SCR-006 | Điểm thấp nhất | S1 × C1 → **1** | Giữ 1 | 1 dialog, dùng lại component tải tệp, chỉ kiểm điều kiện hiện nút và ô lý do. 1 là mức sàn. Giờ 4h → 4.0 h/SWP, cao nhưng vẫn trong khoảng cho FE (trung vị 2.4, cận trên 4.8): màn FE vốn tốn giờ hơn so với SWP. |
| #51 (E01-07a) create_user_account + USR-02 | Quanh trung vị (nửa dưới) | S3 × C2 → **5** | Giữ 5 | Route + hàm DB + Auth Admin API (3 lớp → S3). Có bù trừ (xóa auth user khi DB lỗi) nhưng không có tương tranh → C2, không phải C3. Giờ 12h → 2.4 h/SWP, trong khoảng BE [0.8, 3.2]. |
| #252 (E09-10a) Luồng chính create_accounting_export | Điểm cao nhất | S5 × C3 → **10** | Giữ 10 | Một hàm DB chạm 7+ bảng (khóa ngày, cấp mã, gộp dòng, ghi batch, audit), công thức thuế cho số âm, cạnh tranh với CLS-04. Đúng là issue nặng nhất. Giờ 12h → 1.2 h/SWP, trong khoảng DB [0.78, 3.1]; nhánh lỗi (batch エラー, thông báo) đã tách sang E09-10b. |
| #27 (E00-10) Hàm 業務日 và cấp mã nghiệp vụ | Ngoại lai (điểm cao so với giờ) | S5 × C3 → **10** | Giữ 10 | 4 hàm DB + bảng đếm + helper TypeScript (nhiều thành phần → S5); 100 lời gọi song song không trùng số, biên múi giờ JST (C3). Giờ 8h → 0.8 h/SWP, sát cận dưới DB (0.78) nhưng vẫn trong khoảng. Mỗi hàm nhỏ nên giờ thấp, còn SWP phản ánh rủi ro tương tranh. Sẽ so giờ thực tế ở Sprint 2. |
| #26 (E00-09) Lưu và phát lại Idempotency-Key | Độ tin cậy thấp nhất (medium) | S3 × C3 → **6** | Giữ 6 | Độ tin cậy thấp vì DB design chưa có bảng lưu key (PREMISE S-01). Chỗ hở này đổi *nơi lưu*, không đổi cỡ việc: vẫn 2 lớp (wrapper route + bảng), vẫn có replay / 409 / song song. Giờ 8h → 1.33 h/SWP. Giả lập Sprint 1 tiêu 12h → 2.0 h/SWP, vẫn trong khoảng BE [0.8, 3.2]. |

**Kết luận:** người dùng giữ nguyên cả 5 issue, không đổi Scope / Complexity nào. Vì vậy skill không sinh luật hiệu chỉnh (`calibrationRules` rỗng), trạng thái `accepted`, **0 issue đổi điểm**, tổng giữ 1,247 SWP.

Vì sao giữ:
- Cả 5 issue đều có tỉ lệ giờ / SWP nằm trong [½×, 2×] trung vị của mảng (xem §2). Nghĩa là SWP và giờ ước độc lập vẫn khớp nhau.
- Lý do chấm dựa trên sự kiện cấu trúc kiểm được (số lớp, số bảng, có tương tranh / bù trừ hay không), khớp với `hours_basis` ghi lúc break.
- 5 mẫu phủ cả hai đầu thang (1 và 10), vùng giữa và 2 ca khó (ngoại lai, độ tin cậy thấp). Không ca nào cho thấy skill chấm lệch có hệ thống.

---

## 2. Cách quy ra giờ

### Phương pháp đã chọn: ước giờ trực tiếp từ issue theo band (không quy đổi SWP → giờ)

**Vì sao:**
- Giờ được ước **lúc break backlog**, từ AC và spec LAB-4 của từng issue, trước khi có SWP. Đổi ngược từ SWP sang giờ sẽ bỏ đi thông tin đã có.
- Giữ hai số đo độc lập: giờ (ước trực tiếp) và SWP (skill chấm, không thấy giờ). Hai số khớp nhau thì đáng tin hơn; lệch nhau thì biết ngay issue nào cần xem lại.
- Hệ số giờ / SWP khác nhau theo mảng (màn FE tốn giờ hơn hàm DB cùng điểm), nên một hệ số chung sẽ sai cho cả FE lẫn DB.

### Quy tắc

Mỗi issue lá chỉ nhận 1 trong 5 band. Giờ = code + unit test + tự review của 1 dev trung cấp; **không** gồm thiết kế, IT, ST. Mỗi lá ghi `hours_basis` 1 câu giải thích band.

| Band | Nghĩa (rút từ `hours_basis`) | Ví dụ | Số lá |
|---|---|---|---|
| 2h | Sửa nhỏ 1 chỗ: 1 migration đổi CHECK, 1 chuyển trạng thái đơn giản, 1 API đọc giống mẫu có sẵn | #142 (E05-12), #154 (E06-09) | 7 |
| 4h | 1 hàm / wrapper nhỏ 1–2 nhánh, migration bảng ít ràng buộc, 1 dialog | #14 (E00-03b), #74 (E02-04b) | 60 |
| 8h | 1 hàm DB + route có vài quy tắc, 1 màn thường, migration 4–5 bảng | #4 (E00-02a), #26 (E00-09) | 152 |
| 12h | Nhiều bảng / nhiều nhánh kiểm, có tương tranh hoặc hash chain, màn phức tạp | #7 (E00-02d), #13 (E00-03a) | 53 |
| 16h | Trần của 1 lá. Lớn hơn thì phải tách thành issue cha + sub-issue | #68 (E02-03b) | 1 |
| **Tổng** | | | **273 lá · 2,122h** |

### Áp dụng nhất quán: đối chiếu giờ với SWP

Sau khi có SWP, chạy `tools/check-hours-vs-swp.py` cho cả 273 lá:

1. Tính h/SWP từng lá, lấy **trung vị theo mảng**: BE 1.6 · DB 1.55 · FE 2.4 · INFRA 1.6 · QA 1.33 (trung vị chung 1.6).
2. Lá có h/SWP ngoài **[½×, 2×] trung vị mảng của nó** → PL xem lại `hours_basis` và AC, rồi sửa giờ hoặc ghi lý do giữ.
3. FE có tỉ lệ cao nhất (2.4) là bình thường: màn hình tốn giờ cho bố cục, trạng thái, kiểm nhập liệu, trong khi Scope / Complexity của SWP thấp. Vì vậy phải so theo mảng, không so với trung vị chung.

Kết quả lượt đầu: **5 lá ngoại lai → sửa 2, giữ 3.**

| Issue | Mảng | Giờ → SWP (h/SWP) | Quyết định | Lý do |
|---|---|---|---|---|
| #187 (E07-06d) API INC-05 GET deltas | BE | 4h → 1 (4.0) | **Sửa 4 → 2h** (2.0) | Chỉ là 1 API đọc có lọc + phân quyền, giống các API đọc khác; 4h là ước dư. |
| #300 (E11-16) Hàm job db_dump_offsite + JOB-06 | BE | 4h → 6 (0.67) | **Sửa 4 → 8h** (1.33) | Ước thiếu: ngoài hàm job còn endpoint JOB-06 và gọi runner pg_dump ngoài DB, đồng bộ Storage. |
| #142 (E05-12) Thêm event_type vào CHECK | DB | 2h → 3 (0.67) | Giữ 2h | Skill tính Scope 2 (sửa 2 CHECK + seed) nên SWP tối thiểu là 3. Việc thật chỉ là 1 migration + 2 dòng seed, không có logic (PREMISE H-5 / S-19). 2h đủ. |
| #280 (E11-05) Hàm job sync_operations_purge | DB | 2h → 3 (0.67) | Giữ 2h | Skill tính Scope 2 (hàm job + xử lý lỗi job_runs). Thực tế là 1 câu DELETE theo lô trong khung job có sẵn (#21, E00-05a); làm theo ADR-009 vì chưa có function spec (G-13). |
| #185 (E07-06b) Xác định cause_type / cause_note của delta | BE | 4h → 1 (4.0) | Giữ 4h | Skill thấy "một đoạn logic" (S1 × C1). Nhưng đoạn này cần 1 bảng ưu tiên + 3 join lấy mã chứng từ + cắt note 500 ký tự, và phải test đủ tổ hợp nguyên nhân của 完納奨励金. Giữ 4h để không thiếu giờ UT. |

Sau khi sửa, `generated/hours-vs-swp.json` chỉ còn 3 lá ngoại lai (đều đã ghi lý do giữ). Tổng giờ sau sửa: 2,122h.

---

## 3. Tổng theo epic

| Epic | Số issue lá | Tổng SWP | Tổng giờ | Ghi chú |
|---|---:|---:|---:|---|
| #1 E00 Nền tảng chung | 33 | 160 | 256 | Mọi epic phụ thuộc. Gồm migration 46 bảng, guard, Idempotency-Key (S-01), CI/CD, môi trường Tokyo |
| #41 E01 Đăng nhập & phân quyền | 14 | 62 | 124 | Guard / middleware phiên nằm ở E00 (#24) |
| #58 E02 Người tham gia & tư cách | 20 | 76 | 164 | Có lá 16h duy nhất (#68 duyệt tư cách, tương tranh 2 người duyệt) |
| #84 E03 Lô hàng | 13 | 52 | 104 | Hàng đợi offline dùng chung nằm ở E11 |
| #99 E04 Giao dịch 相対 / せり | 20 | 86 | 164 | Theo FN / SERI-01 (H-6) |
| #123 E05 Giao hàng | 17 | 90 | 142 | Lock order theo FN (H-1, H-4); OQ-26 còn mở |
| #143 E06 Đối soát, khóa ngày, điều chỉnh, tranh chấp | 23 | 104 | 178 | |
| #169 E07 完納奨励金 & 入金 | 39 | 149 | 242 | **Ràng buộc 完納奨励金**: không gộp, tách theo từng biến nghiệp vụ; nhiều lá nhất sau E11 |
| #217 E08 Thông báo | 11 | 51 | 76 | Chưa chọn dịch vụ email (#334) |
| #229 E09 Báo cáo & xuất CSV kế toán | 26 | 134 | 196 | Có issue nặng nhất #252 (10 SWP) |
| #260 E10 Audit | 13 | 61 | 104 | Hàm audit_append dùng chung nằm ở E00 (#13) |
| #275 E11 Offline, giám sát, lưu trữ chứng từ, migration | 44 | 222 | 372 | **Lớn nhất** (18 % giờ); có DR (OQ-04) và loader migration (QA-010) chờ khách |
| **Tổng** | **273** | **1,247** | **2,122** | + 39 issue cha + 12 epic = 324 issue dev |

---

## 4. So với estimate LAB-1

LAB-1 = WBS-4 "Lập trình + UT" trong `project/01_management/estimate-wbs.md` của repo bài LAB-1 (bản v1.0, 2026-10-27), PD theo FG, quy 1 PD = 8h. LAB-5 = tổng giờ lá theo epic. FG-01〜FG-11 ứng 1-1 với E01〜E11; "nền tảng chung 30 PD" ứng với E00.

| Phần (epic / FG) | LAB-1 PD (giờ) | LAB-5 giờ | Chênh | Vì sao |
|---|---:|---:|---:|---|
| E00 / nền tảng chung | 30 (240) | 256 | +16h (+7 %) | Duy nhất tăng. Thêm việc LAB-1 chưa tách: CI/CD #35, #36, #37 (20h), môi trường Tokyo #38 (12h), Idempotency-Key #26 (8h, **S-01**), pg_net / Vault ở migration (**S-02**). Môi trường và CD một phần trùng WBS-6 (hạ tầng) của LAB-1 |
| E01 / FG-01 | 20 (160) | 124 | −36h (−22 %) | Guard và middleware phiên chuyển sang E00 (#24). Chính sách mật khẩu theo API / DD (**S-04**) không đổi khối lượng |
| E02 / FG-02 | 48 (384) | 164 | −220h (−57 %) | F-004 được xếp XL 28 PD vì còn ẩn số; LAB-4 đã chốt FN duyệt / hết hạn, job dùng khung chung E00. Đổi vai trò nhận (**S-07**, **S-08**, **G-03**) chỉ là chỉnh nhỏ |
| E03 / FG-03 | 39 (312) | 104 | −208h (−67 %) | Hàng đợi offline của màn lô tính ở E11 (#281). Chiều gọi sync_apply_operation đã chốt theo FN (**S-10**), view lịch sử tự định nghĩa (**S-11**) |
| E04 / FG-04 | 52 (416) | 164 | −252h (−61 %) | F-011 XL 25 PD lúc chưa có thiết kế chi tiết; nay theo FN / SERI-01 (**H-6**, **S-12**, **S-13**) |
| E05 / FG-05 | 45 (360) | 142 | −218h (−61 %) | Replay offline ở E11; lock order và chữ ký hàm đã chốt (**H-1**, **H-3**, **H-4**, **S-14〜S-18**). Thêm #142 (E05-12, **H-5** / **S-19**) +2h |
| E06 / FG-06 | 60 (480) | 178 | −302h (−63 %) | F-021 XL 25 PD; chiều gọi delta và bảng ghi chú tranh chấp đã chốt (**S-21**, **S-22**, **S-24**) |
| E07 / FG-07 | 65 (520) | 242 | −278h (−53 %) | Ràng buộc 完納奨励金 tách 39 lá nên giảm ít hơn các epic nghiệp vụ khác. Khóa kỳ và version quy tắc đã chốt (**H-2**, **H-7**, **S-25〜S-30**) |
| E08 / FG-08 | 20 (160) | 76 | −84h (−52 %) | Event type bổ sung chỉ là seed / CHECK (**S-31**); adapter email chờ chọn nhà cung cấp (#334) |
| E09 / FG-09 | 40 (320) | 196 | −124h (−39 %) | Giảm ít vì báo cáo nhiều tham số (**S-35**, **S-36**) và job bản chụp không có FN (**G-10**). Bỏ rpt06 khỏi bản chụp (**H-8**), BOM là cấu hình (**H-9**) |
| E10 / FG-10 | 22 (176) | 104 | −72h (−41 %) | audit_append / writeAuditLog dùng chung đã tính ở E00 (#13, #14). Archive 1 file / tháng (**H-10**, **S-38**) |
| E11 / FG-11 | 65 (520) | 372 | −148h (−28 %) | Giảm ít nhất: gom offline của E03 / E05 về đây, thêm runner DR #300, #301 và công cụ migration #319 (một phần LAB-1 để ở WBS-6 / WBS-8). Nhiều chỗ hở nhất (16 spec gap, **S-41〜S-48**, **G-13〜G-15**) |
| **Tổng** | **506 (4,048)** | **2,122** | **−1,926h (−48 %)** | Quy 6h tập trung / ngày: LAB-5 = **354 PD** so với 506 PD → **−30 %** |

### Vì sao LAB-5 thấp hơn 48 % (30 % khi tính 6h tập trung / ngày)

1. **Độ chi tiết khác nhau.** LAB-1 xếp cỡ S / M / L / XL theo feature, trước 詳細設計, nên mỗi cỡ đã chứa phần ẩn số. LAB-5 đếm từng lá đã có AC và spec LAB-4.
2. **LAB-5 chỉ đếm việc có trong danh sách.** Giờ lá = code + UT + tự review. **Không** gồm: làm lại khi spec đổi, sửa bug phát hiện ở IT, vòng review / chỉnh sửa PR, họp, hỏi đáp spec. Các việc này LAB-1 đã ngầm tính trong PD.
3. **Ngày làm việc thực.** 1 PD của LAB-1 = 8h có mặt; LAB-5 lập kế hoạch 6h tập trung / ngày. So cùng 6h / ngày thì chênh còn −30 %.
4. **詳細設計 LAB-4 đã gỡ ẩn số.** Thứ tự khóa, chữ ký hàm, mã lỗi, quyền đã chốt (H-1〜H-12). Trong 48 điểm sửa spec (S-01〜S-48), nhiều điểm chỉ là đồng bộ câu chữ giữa các tài liệu; số ít thêm việc thật (S-01, S-19).
5. **E00 tăng nhẹ** vì thêm CI/CD, môi trường Tokyo, Idempotency-Key (S-01) là việc có thật nhưng LAB-1 chưa tách thành dòng riêng.

### Khuyến nghị

- **Giữ ngân sách LAB-1 (506 PD WBS-4) làm mốc hợp đồng.** Không cắt ngân sách theo con số LAB-5.
- **Kế hoạch sprint dùng LAB-5 + đệm ~30 %** cho việc không có trong danh sách (rework, bug IT, review, họp, trả lời câu hỏi khách). 2,122h × 1.3 ≈ 2,759h, vẫn dưới 4,048h của LAB-1.
- **Xem lại sau 2–3 sprint** với velocity thực tế (Sprint 1 giả lập: xong 112 / 134 SWP = 84 %). Nếu velocity < 85 % kéo dài, tăng đệm hoặc thêm người BE (xem `progress-report.md`).

---

## Lịch sử thay đổi

| Ngày | Nội dung | Người |
|---|---|---|
| 2026-11-11 | Bản đầu: calibration SWP, quy tắc giờ theo band, tổng theo epic, so với LAB-1 | PL |
