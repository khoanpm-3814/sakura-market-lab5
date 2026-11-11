# Task breakdown — từ spec LAB-4 tới backlog trên GitHub Project

Backlog: 12 epic (E00〜E11), 324 issue dev (12 epic + 39 issue cha + 273 issue lá) và 15 issue làm rõ (#325〜#339). Tổng 2,122 giờ, 1,247 SWP.
Nguồn dữ liệu: `backlog-data/E*.json`, `generated/report-tables.md`. Thay đổi so với spec LAB-4 ghi ở `PREMISE.md`.

## 1. Nguyên tắc chia task

### 1.1 Độ mịn — dừng chia ở đâu

| Quy tắc | Nội dung |
| --- | --- |
| Đơn vị lá | Một việc 1 dev làm xong trọn: một hàm DB, một route API, một màn, một job hoặc một bộ test vector. Có tiêu chí chấp nhận kiểm được. |
| Giờ của lá | ≤ 16h, chọn một band **2 / 4 / 8 / 12 / 16**. Giờ = code + unit test + tự review của 1 dev trung cấp; không gồm thiết kế, IT, ST. Giờ ước trực tiếp lúc break, không quy đổi từ SWP (PREMISE P-1). |
| Khi nào tạo sub-issue | (a) việc ước > 16h, hoặc (b) việc trộn nhiều mảng BE / DB / FE / QA. Khi đó issue thành **issue cha**, không mang giờ; mỗi sub-issue là lá một mảng. Có 39 issue cha, 11 trong số đó trộn mảng. |
| Test | Unit test nằm trong DoD của từng lá, không tách issue. Chỉ tách issue QA riêng cho **test vector nghiệp vụ** (công thức, tương tranh, tích hợp chéo epic): 18 lá QA, 152h. |
| Không thành issue | Việc ngoài lập trình + UT (load test, diễn tập, cutover, việc nghiệp vụ của khách), việc của epic khác (ghi rõ epic sở hữu), hoặc chờ khách trả lời. Xem cột cuối ở §2. |
| Mảng | BE 140 lá / 1,004h · DB 44 / 338h · FE 64 / 572h · QA 18 / 152h · INFRA 7 / 56h. |

### 1.2 Definition of Done (dán trong thân mọi issue)

> Code + unit test (happy path, lỗi nghiệp vụ, quyền) pass trên CI · review được duyệt · tiêu chí chấp nhận kiểm được trên môi trường dev · spec LAB-4 liên quan đã cập nhật nếu có thay đổi

Thân issue còn có: epic, key, mảng, ưu tiên, giờ + căn cứ giờ, mô tả, tiêu chí chấp nhận (checkbox), mã spec LAB-4, phụ thuộc (`#số (key)`).

### 1.3 Epic → issue → sub-issue trên Project

| Thành phần | Cách dùng |
| --- | --- |
| Cấp bậc | Dùng **sub-issue gốc của GitHub**: epic → issue → sub-issue (tối đa 3 cấp). Issue làm rõ là sub-issue của epic. |
| Label | `type:epic` / `type:issue` / `type:sub-issue` / `type:clarify` · `epic:E00`〜`epic:E11` · `disc:BE` / `DB` / `FE` / `QA` / `INFRA` · `priority:must` / `should` · `constraint:完納奨励金` (39 lá của E07). |
| Field **Loại** | Epic / Issue / Sub-issue. |
| Field **Giờ ước lượng** | Chỉ ghi ở lá. Issue cha và epic để trống (thân issue ghi "tổng của sub-issue"). |
| Field **SWP** | Lá: điểm đã review từ skill estimate-swp (level medium, 5 issue mẫu, calibration `accepted`). Issue cha / epic = **tổng SWP của con**. |
| Field **Iteration** | Sprint 1〜10, mỗi sprint 2 tuần, từ 2027-02-01. |
| Field **Status** | Todo → In Progress → In Review → Done. |
| Field **Phụ trách (giả định)** | TL, BE-1, BE-2, FE-1, FE-2 (full-stack), QA-1 — vai trò giả định để lập kế hoạch, không phải người thật. |
| Issue làm rõ (`type:clarify`) | Việc của PL / BrSE với khách: **không có giờ, không SWP, không xếp sprint**; Phụ trách = TL. |

## 2. Spec → issue

Issue liệt kê theo dải số liên tiếp; "cha (con)" là issue cha và các sub-issue của nó. Lá / giờ / SWP lấy từ bảng epic-totals.

| Spec | Epic | Issue / sub-issue | Lá · giờ · SWP | Issue làm rõ | Phần spec chưa thành issue và vì sao |
| --- | --- | --- | --- | --- | --- |
| ADR-001〜010, common-spec, TBL nền | #1 E00 Nền tảng chung | #2〜#40; cha: #3 (#4〜#11), #12 (#13〜#14), #15 (#16〜#19), #20 (#21〜#22), #29 (#30〜#33), #34 (#35〜#37) | 33 · 256h · 160 | #325 | ATT-03〜06, JOB-02〜04, lưu trữ lạnh / khôi phục → E11 (F-035); E00 chỉ làm phần tải lên ATT-01 / 02. Kiểm chuỗi / archive / tra cứu audit → E10. notify_event → E08. Seed rule_versions, notification_settings → E07 / E08 nạp cùng hàm dùng. JOB-06 + DR Osaka → E11, chờ OQ-04. PWA + IndexedDB → E11. Load test, diễn tập restore, uptime monitor → ST / vận hành. |
| F-001, F-002 | #41 E01 Đăng nhập & phân quyền | #42〜#57; cha: #42 (#43〜#44), #50 (#51〜#57) | 14 · 124h · 62 | #326 | Guard requireApiUser / middleware phiên đã ở E00-07 (mọi epic dùng). Thông báo security_event → E08. Cảnh báo bảo mật bất thường → ops_watchdog E11. Quên / đổi mật khẩu tự phục vụ: không có trong 37 F, chờ OQ-15 (nếu cần là CR). |
| F-003〜F-006 | #58 E02 Người tham gia & tư cách | #59〜#83; cha: #60 (#61〜#65), #66 (#67〜#71), #72 (#73〜#74), #77 (#78〜#79), #80 (#81〜#82) | 20 · 164h · 76 | #327, #328 | NTF-01 / 02, SCR-003, gửi email → E08 (E02 chỉ gọi notify_event). Cảnh báo job eligibility_daily quá hạn → E11. Nạp tư cách từ nguồn cũ → migration E11. |
| F-007〜F-010 | #84 E03 Lô hàng | #85〜#98; cha: #94 (#95〜#97) | 13 · 104h · 52 | — | Hàng đợi offline SCR-009, SYNC-01 / 02 → E11 (E03-02 dùng chung đường code). In tag / mã vạch, danh mục 品目区分 / 等級: không có trong 37 F, chờ OQ-16. Xem ảnh 受入票 (ATT-03) → E11. |
| F-011〜F-014 | #99 E04 Giao dịch 相対 / せり | #100〜#122; cha: #102 (#103〜#104), #113 (#114〜#116), #118 (#119〜#120) | 20 · 164h · 86 | — | SCR-013 gộp vào SCR-012 (wireframe Option B), làm ở #115. Sửa kết quả sau 確定 → E06 (F-021). Chốt 相対 / ghi せり khi mất mạng: ngoài phạm vi (QA-005), chỉ chặn phía client. OCR / suy luận người thắng せり: ngoài phạm vi (SCOPE-OUT-02, CAP-HUMAN-01). Hai người xác nhận せり: chờ OQ-19 (PREMISE G-17). |
| F-015〜F-018 | #123 E05 Giao hàng | #124〜#142; cha: #124 (#125〜#128), #135 (#136〜#138) | 17 · 142h · 90 | #329 | Phần offline (IndexedDB, SCR-021, SYNC-01 / 02, X-Resolves-Op-Id) → E11; E05 chỉ gọi sync_apply_operation. Xem ảnh (ATT-03) → E11. Phiếu điều chỉnh số lượng → E06 (F-021). Tranh chấp từ ngoại lệ → E06 (F-022). Báo cáo tồn đọng, xuất kế toán → E09. Dữ liệu giao hàng cũ lúc cutover → E11, chờ OQ-12. |
| F-019〜F-022 | #143 E06 Đối soát, khóa ngày, điều chỉnh, tranh chấp | #144〜#168; cha: #144 (#145〜#146), #155 (#156〜#158) | 23 · 178h · 104 | #330 | SCR-004 / ELG-02 (màn chung F-004 / F-021) giả định E02 làm; E06 chỉ cấp COR-03 lọc 申請中. DLV-06 thuộc E05, E06 chỉ nối hiển thị. Job daily_report_build → E09. ROLE-006 xác nhận hoàn tất tranh chấp giao hàng: chưa có API → #330. |
| F-023, F-024, F-025, F-041 | #169 E07 完納奨励金 & 入金 | #170〜#216; cha: #173 (#174〜#178), #179 (#180〜#182), #183 (#184〜#187), #188 (#189〜#190), #192 (#193〜#195), #198 (#199〜#205), #206 (#207〜#211), #212 (#213〜#215) | 39 · 242h · 149 | #331, #332 | 試算 1 tháng tải năm 3 ≤ 5 phút (AC-17): đo ở load test ST; #181 chỉ bảo đảm set-based + review EXPLAIN. AUD-02 → E10. RPT 07 / FORM-INC-01 → E09. Ghi rule_version_id vào settlement_lines do hàm E05 / E06 làm (gọi #172). Giá trị bảng bậc / N thật (OQ-14), xác nhận A-06 / A-07 (OQ-06 / 07): seed tạm ở #216, khách trả lời khác → CR. |
| F-026, F-027 | #217 E08 Thông báo | #218〜#228 (không có issue cha) | 11 · 76h · 51 | #333, #334 | Job phát eligibility_expiry_notice, delivery_backlog_notice → E02 / E05. Số thông báo chưa đọc trên SCR-002: API thuộc E02 / UI chung E00, #223 trả sẵn số để dùng lại. Cảnh báo A-5 → E11. SMS / FAX: ngoài phạm vi (A-04). |
| F-028〜F-030 | #229 E09 Báo cáo & xuất CSV kế toán | #230〜#259; cha: #232 (#233〜#237), #238 (#239〜#242), #247 (#248〜#250), #251 (#252〜#253) | 26 · 196h · 134 | #335, #336 | Vô hiệu batch khi mở khóa ngày nằm trong CLS-04 #148 (E06-03). Cảnh báo A-3 / A-4 → E11. Seed export_failed / job_failed → E08-02. Bảng snapshot báo cáo: chỉ làm nếu ST đo RPT-02 không đạt p95 ≤ 2 giây. Đo NFR-007 / NFR-004 → ST. Nhập CSV vào hệ thống kế toán (QA-009): ngoài hệ thống. Nút dựng lại báo cáo (OQ-25): chưa có trong spec. |
| F-031, F-032 | #260 E10 Audit | #261〜#274; cha: #269 (#270〜#272) | 13 · 104h · 61 | #337, #338 | Bảng audit, trigger chặn sửa, audit_append, writeAuditLog đã ở E00-03a / 03b. Lời gọi audit_append trong từng hàm thuộc epic sở hữu; #274 chỉ kiểm phủ. Cảnh báo A-6 / A-7 → E11. Neo last_row_hash gửi ROLE-011: không có API / màn / job → #338. Đo verify 40 triệu dòng, AUD-01 p95 → ST. |
| F-033〜F-036 | #275 E11 Offline, giám sát vận hành, lưu trữ chứng từ, migration | #276〜#324; cha: #281 (#282〜#285), #289 (#290〜#291), #296 (#297〜#299), #316 (#317〜#318), #319 (#320〜#323) | 44 · 372h · 222 | #339 | Đảo lần giao replay muộn khi xung đột: trong DLV-03 (E05); E11-08 chỉ test tích hợp. sync_apply_operation trong create_lot / SCR-009 / SCR-019 bản online → E03 / E05. Tải lên ATT-01 / 02 đã ở E00-04. Event type xung đột / ops_alert → E08-02. Chạy リハーサル D−7, 本番 D−1, go-live: giai đoạn cutover. Đối chiếu mẫu ≥ 30 người tham gia: việc nghiệp vụ ROLE-005. Diễn tập NFR-014, đo uptime, restore DR → ST / vận hành. A-10 / A-11 dùng metrics Supabase / Vercel, chỉ cấu hình kênh ở E11-18. Danh sách giao dịch cũ còn phải giao: chờ OQ-12. |

## 3. Hạng mục chịu ràng buộc đặc thù của đề — Product A 完納奨励金

Mọi lá dưới đây thuộc #169 (E07), mang label `constraint:完納奨励金`. Nhóm theo **biến nghiệp vụ** mà issue khóa lại.

| Ràng buộc (biến nghiệp vụ) | Issue | SWP | Giờ | Vì sao tách riêng |
| --- | --- | --- | --- | --- |
| Dữ liệu thưởng / 入金 bất biến, chỉ thêm (append-only) | #170 (E07-01) | 6 | 8 | Mọi sửa sai đi bằng dòng đảo / delta; trigger chặn sửa là nền cho cả epic, phải có trước và test riêng. |
| Tháng giao dịch gốc (A-07) | #174 (E07-04a) | 3 | 4 | P gom theo `target_period` của giao dịch gốc, không theo ngày giao / ngày nhập. Sai biến này lệch cả kỳ, cần test vector riêng. |
| Phiên bản quy tắc theo ngày | #172 (E07-03), #175 (E07-04b), #216 (E07-15) | 6 | 10 | Một tháng có thể có 2 phiên bản quy tắc; mỗi dòng 精算 tra phiên bản theo 業務日 rồi tách Pₖ. Seed v1 tách riêng vì giá trị thật còn chờ OQ-14. |
| Bậc tỷ lệ theo P tổng tháng | #176 (E07-04c) | 2 | 4 | Bậc chọn theo P **tổng tháng**, nhưng áp cho từng phần Pₖ theo phiên bản; dễ nhầm nên tách để kiểm biên bậc. |
| 入金 đủ hạn và 完納 | #171 (E07-02), #177 (E07-04d) | 6 | 8 | 支払期日 của kỳ quyết định 入金 nào được tính vào R; xét 完納 phụ thuộc hạn này. |
| Thuế 110/100 (A-05) và làm tròn | #178 (E07-04e) | 3 | 4 | Hệ số thuế và làm tròn xuống **1 lần / người / tháng**; làm tròn sai chỗ lệch vài yên mỗi người. |
| 試算 → 確定 | #180, #181, #182 (E07-05a〜c), #189, #190 (E07-07a〜b), #208 (E07-13b, SCR-028) | 26 | 38 | Hai bước có guard và thứ tự khóa kỳ khác nhau; 確定 phải chặn khi dữ liệu đổi sau 試算 (M_INC_51). Tách hàm / route / màn để review khóa riêng. |
| Delta sang kỳ sau (A-06) | #184, #185, #186, #187 (E07-06a〜d) | 11 | 22 | Thay đổi sau 確定 không sửa kỳ cũ mà sinh delta ở kỳ nhận, lúc 試算 kỳ đó (S-21, S-26). #186 là helper khóa shared mà E05 / E06 cũng gọi. |
| Import 入金 | #193, #194, #195 (E07-09a〜c), #196 (E07-10), #197 (E07-11), #207 (E07-13a, SCR-027) | 29 | 52 | CSV từ kế toán: parse, kiểm từng dòng gom lỗi, chế độ 通常 / 追加入金 cho kỳ đã 確定, hủy bằng dòng đảo. Mỗi bước có lỗi riêng nên tách lá. |
| Maker-checker phiên bản quy tắc | #199〜#205 (E07-12a〜g), #210, #211 (E07-13d〜e, SCR-030 / 031) | 34 | 52 | Soạn (ROLE-007) và duyệt (ROLE-008) do 2 người; trạng thái 下書き → 承認待ち → 承認済 → 発効, cộng rollback / 廃止 và job kích hoạt 02:00. Mỗi chuyển trạng thái một hàm + route. |
| Tra kết quả người tham gia × tháng × phiên bản | #191 (E07-08), #209 (E07-13c, SCR-029) | 7 | 16 | Phải chỉ ra được mỗi phần thưởng dùng phiên bản nào (rule_version_id trên incentive_line_parts) để giải thích cho người tham gia. |
| Test vector nghiệp vụ | #213 (E07-14a), #214 (E07-14b), #215 (E07-14c) | 16 | 24 | Bộ vector công thức (INC-EDGE-01 / 03, AC-2〜7), delta / 入金 (INC-EDGE-02, 追加入金, hủy) và tương tranh khóa kỳ. Chạy chéo nhiều hàm nên là issue QA riêng. |
| **Tổng E07** | **39 lá** | **149** | **242** | |

**Vì sao không gộp thành một task lớn.** E07 có 39 lá, 242h, 149 SWP — nhiều issue lá thứ hai sau E11 (44 lá); theo giờ đứng sau E11 và E00. Công thức 完納奨励金 gồm nhiều biến độc lập; mỗi biến có thể sai riêng và lệch tiền theo cách riêng. Một task "tính thưởng" sẽ vượt xa 16h, không review được theo từng biến, và khi sai sẽ không biết hỏng ở biến nào. Tách theo biến cho phép: mỗi lá có test vector nhắm đúng biến đó; khách trả lời OQ-06 / 07 / 14 thì chỉ sửa đúng lá liên quan; và tiến độ trên Project phản ánh đúng phần rủi ro cao nhất của đề.

## 4. Chỗ hở hoặc mâu thuẫn của spec LAB-4 phát hiện khi break

87 chỗ: 48 đã sửa thiết kế, 18 giả định, 15 tạo issue làm rõ, 6 để mở. Chi tiết "trước → sau" của từng S-xx / G-xx ở `PREMISE.md`.

| # | Spec | Chỗ hở / mâu thuẫn | Xử lý |
| --- | --- | --- | --- |
| E00-g1 | API-COMMON-CONVENTIONS No.14 / TRD-03 bước 3, 6 | Spec bắt lưu Idempotency-Key + hash + response, DB không có bảng; sync_operations chỉ cho offline. | đã sửa thiết kế (→ PREMISE S-01) |
| E00-g2 | ADR-009 bảng job ↔ FN-LIST | Job sync_operations_purge, attachment_temp_purge có lịch nhưng không có FN. | tạo issue làm rõ (#325) |
| E00-g3 | DB-TABLES-LIST ↔ ADR-009 Decision 2 | Hai cách đặt tên hàm job; migration lịch cần một tên. | giả định (→ PREMISE G-01) |
| E00-g4 | DB-INITIAL-DATA §1 bước 100 | Thiếu pg_net và Supabase Vault cho job gọi endpoint nội bộ. | đã sửa thiết kế (→ PREMISE S-02) |
| E00-g5 | DB-TABLES-LIST §3 | Tiêu đề 44 bảng, tổng 46, đánh số nhảy. | đã sửa thiết kế (→ PREMISE S-03) |
| E01-g1 | ARCH-OVERVIEW §8 ↔ USR-02 / USR-06 / DD-F001 §5 | Hai chính sách mật khẩu khác nhau. | đã sửa thiết kế (→ PREMISE S-04) |
| E01-g2 | DD-F001 §2.4 | Hết khóa không reset bộ đếm nên sai 1 lần là khóa lại; DD tự ghi là câu hỏi mở nhưng chưa vào open-questions. | tạo issue làm rõ (#326) |
| E01-g3 | DD-F002 §2 / §3 | Lỗi "không có thay đổi" của tài khoản dùng mã M_LOT_17 của lô. | đã sửa thiết kế (→ PREMISE S-05) |
| E01-g4 | DD-F002 §1, §2 | DD ghi create / update_user_account "dự kiến" dù FN v1.1 đã có. | đã sửa thiết kế (→ PREMISE S-06) |
| E01-g5 | COMMON-SPEC CS-02 ↔ DD-F001 §1 | Không rõ [延長] phiên gọi API nào. | giả định (→ PREMISE G-02) |
| E02-g1 | DD-F004 daily-expiry-job §3.2 ↔ DB-INITIAL-DATA §2.5 | Seed người nhận eligibility_expiring thiếu ROLE-010. | đã sửa thiết kế (→ PREMISE S-07) |
| E02-g2 | API-LIST ELG-04 ↔ DD-F004 approval §5 | Hai danh sách vai trò cho ELG-04. | đã sửa thiết kế (→ PREMISE S-08) |
| E02-g3 | API-LIST PTY-01 ↔ SCREEN-LIST §3 | PTY-01 đã bỏ ROLE-006 nhưng menu vẫn đề xuất SCR-005 cho ROLE-006. | tạo issue làm rõ (#327) |
| E02-g4 | DD-F004 approval §4 ↔ DB-TABLES-LIST No.6 | DD không nêu ca hỏi ngày D < valid_from của kỳ 有効(予定). | giả định (→ PREMISE G-03) |
| E02-g5 | F-004 / FN eligibility_request_decide | Thông báo kết quả gửi requested_by nhưng notify_event không nhận người nhận cụ thể. | tạo issue làm rõ (#328) |
| E03-g1 | DD-F007 §3.1 ↔ API-LIST LOT-04 | DD guard LOT-04 khác API-LIST đã chốt. | đã sửa thiết kế (→ PREMISE S-09) |
| E03-g2 | DD-F007 §1.1 / DD-F016 §2.1 ↔ FN create_lot / record_delivery | Chiều gọi sync_apply_operation ngược nhau giữa DD và FN. | đã sửa thiết kế (→ PREMISE S-10) |
| E03-g3 | DD-F007 §5.2 / LOT-05 | View v_lot_qty_history không được FN nào định nghĩa. | đã sửa thiết kế (→ PREMISE S-11) |
| E03-g4 | OQ-08 / PREMISE A-08 | Bắt buộc 下見 trước 公開 vẫn là giả định chờ khách. | để mở — không chặn sprint; giữ thiết kế hiện tại, nếu khách cần 公開 trực tiếp thì thêm đường có lý do. |
| E04-g1 | DD-F013 §1 ↔ FN record_seri_result / SERI-01 v1.1 | DD lỗi thời: thuế, kiểu seri_slot_no, mã lỗi, kiểm trùng. | đã sửa thiết kế (→ PREMISE S-12) |
| E04-g2 | FN check_trade (khác biệt so với prototype) | Còn câu cũ trái bản 1.2 (lô 確定 còn số lượng). | đã sửa thiết kế (→ PREMISE S-13) |
| E04-g3 | TRD-08 ↔ FN record_seri_result / decide_correction | Lọc audit `trade.*` làm lịch sử せり thiếu bước tạo. | giả định (→ PREMISE G-04) |
| E04-g4 | FN create_trade_draft / TRD-01 | Bấm đúp tạo 2 nháp; key chỉ khuyến nghị, chưa có nơi lưu. | giả định (→ PREMISE G-05) |
| E04-g5 | F-013 せり (US-04-05, R-11) | Chưa có phân tích chức năng chi tiết; mọi quy tắc mượn F-011. | để mở — không chặn sprint; nếu khách thêm luật riêng (vd 2 người xác nhận OQ-19, giả định G-17) thì CR nhỏ cho #111. |
| E05-g1 | DLV-03 bước 4.1–4.2 ↔ FN record_delivery | API khóa ngược thứ tự chuẩn của ADR-003. | đã sửa thiết kế (→ PREMISE S-14) |
| E05-g2 | FN README §2 No.5 ↔ 3 FN giao hàng ↔ E07-06c | 3 FN không lấy khóa shared incentive_period; vị trí khóa không thống nhất. | đã sửa thiết kế (→ PREMISE S-15) |
| E05-g3 | DD-F016 / DD-F033 ↔ DLV-03 / FN | Header replay X-Queued khác X-Sync-Replay. | đã sửa thiết kế (→ PREMISE S-16) |
| E05-g4 | DLV-03 bước 4 ↔ FN record_delivery | Chữ ký rpc khác nhau; ack_at lấy giờ client hay server. | đã sửa thiết kế (→ PREMISE S-17) |
| E05-g5 | DD-F016 §2 ↔ FN record_delivery / DLV-03 | Ba lỗi có mã / HTTP status khác nhau. | đã sửa thiết kế (→ PREMISE S-18) |
| E05-g6 | TBL-notification_settings CHECK ↔ FN giao hàng | Thiếu delivery_exception, sync_conflict → notify_event rollback cả thao tác. | đã sửa thiết kế (→ PREMISE S-19) |
| E05-g7 | FN delivery_backlog_notice ↔ initial-data | FN và seed ghi người nhận khác nhau. | giả định (→ PREMISE G-06) |
| E05-g8 | DD-F016 §4.7 (ma trận F-017) | Ngoại lệ có tranh chấp cần ROLE-006 xác nhận hoàn tất nhưng không có API / hàm. | tạo issue làm rõ (#329) |
| E05-g9 | FN record_delivery_exception ↔ DD-F016 §4 | Tệp đính kèm gửi cùng request hay tải sau: 3 chỗ nói khác nhau. | đã sửa thiết kế (→ PREMISE S-20) |
| E05-g10 | OQ-26 (căn cứ P / hóa đơn / kế toán) | Chưa chốt P = tổng làm tròn từng lần giao hay tiền giao dịch lúc 確定. | giả định (→ PREMISE G-16) |
| E05-g11 | OQ-17 (ảnh / lý do của ngoại lệ) | Khách chưa trả lời. | giả định (→ PREMISE G-07) |
| E06-g1 | FN decide_correction bước 20 ↔ FN record_incentive_delta | Hàm nguồn gọi thẳng record_incentive_delta → delta 2 lần hoặc vào kỳ chưa khóa. | đã sửa thiết kế (→ PREMISE S-21) |
| E06-g2 | DD-F022 §3.2 ↔ TBL-dispute_notes / DSP-05 | DD nói không có bảng ghi chú, DB / API đã có. | đã sửa thiết kế (→ PREMISE S-22) |
| E06-g3 | DD-F022 §2.4 (CAP-HUMAN-01) | ROLE-006 xác nhận hoàn tất tranh chấp giao hàng: không có API / cột / trạng thái. | tạo issue làm rõ (#330) |
| E06-g4 | DD-F019 §1.4 ↔ API-LIST CLS-01 / 02 | Quyền xem của ROLE-010 / 011 khác nhau. | đã sửa thiết kế (→ PREMISE S-23) |
| E06-g5 | FN unlock_business_day bước 6 ↔ CHECK | business_day_unlocked không có trong CHECK → thông báo bị bỏ qua. | đã sửa thiết kế (→ PREMISE S-24) |
| E06-g6 | SCREEN-LIST SCR-026 ↔ DD-F022 | Thiết bị: PC hay PC + Tablet. | giả định (→ PREMISE G-08) |
| E06-g7 | OQ-20 (ROLE-005 xem phiếu người khác) | Phạm vi xem COR-03 / 04 chờ khách. | để mở — #159 (E06-11) làm theo "chỉ phiếu của mình", điều kiện lọc gom một chỗ để đổi nhanh. |
| E07-g1 | DD-F023 / DD-F041 ↔ FN-incentive / FN-payment | Hai bộ Message ID cho cùng điều kiện. | đã sửa thiết kế (→ PREMISE S-25) |
| E07-g2 | FN record_incentive_delta ↔ decide_correction, DD-F041, README No.57 | Ai được gọi record_incentive_delta: mâu thuẫn giữa 4 tài liệu. | đã sửa thiết kế (→ PREMISE S-26) |
| E07-g3 | FN calculate_incentives bước 5 (M_INC_70) | Luật "kỳ trước phải 確定 mới 試算 kỳ sau" do FN tự thêm, chưa hỏi khách. | tạo issue làm rõ (#331) |
| E07-g4 | FN import_payments bước 11 (M_PAY_71) | Chặn 入金 của người không có 精算 trong tháng: luật suy ra, trái với incentive_compute. | tạo issue làm rõ (#332) |
| E07-g5 | DD-F041 bước 2.1 / 2.9 ↔ FN import_payments | Cách khóa kỳ, thời điểm lưu file, mã dry_run khác nhau. | đã sửa thiết kế (→ PREMISE S-27) |
| E07-g6 | DD-F025 v1.0 ↔ API-LIST v1.1 RUL-07 / 08 | DD chưa tách rollback / 廃止; test viewpoint sai theo thiết kế mới. | đã sửa thiết kế (→ PREMISE S-28) |
| E07-g7 | TBL-settlement_lines / TBL-payments Note | Trigger chỉ cho gán incentive_delta_id 1 lần, re-試算 cần gán lại. | đã sửa thiết kế (→ PREMISE S-29) |
| E07-g8 | FN confirm_incentives bước 8 | Guard M_INC_51 hở vì hàm ghi của E05 / E06 không lấy khóa shared. | đã sửa thiết kế (→ PREMISE S-30) |
| E07-g9 | SCR-029 ↔ DD-F023 §6 / AUD-02 | SCR-029 có dùng AUD-02 hay không. | giả định (→ PREMISE G-09) |
| E08-g1 | TBL-notification_settings CHECK ↔ unlock_business_day, DD-F033 §3.4 | Event mở khóa ngày và xung đột đồng bộ thiếu trong CHECK. | đã sửa thiết kế (→ PREMISE S-31) |
| E08-g2 | CHECK ↔ DD-F025 §2.2 / FN quy tắc | CHECK có 3 event của quy tắc nhưng FN không gọi notify_event; rule_approval_overdue không job nào sinh (OQ-23). | tạo issue làm rõ (#333) |
| E08-g3 | A-04 email giao dịch | Chưa chọn nhà cung cấp SMTP API, domain gửi, SPF / DKIM, nơi giữ khóa. | tạo issue làm rõ (#334) |
| E08-g4 | DD-F026 §5.2 ↔ FN list No.84 | DD ghi notification_setting_update "dự kiến" dù FN đã có. | đã sửa thiết kế (→ PREMISE S-32) |
| E09-g1 | DD-F030 §2.8 ↔ OQ-22 / OQ-03 | CSV kế toán có BOM hay không. Trong lúc chờ khách: mặc định không BOM (PREMISE S-50, H-9). | tạo issue làm rõ (#335) |
| E09-g2 | FN create_accounting_export ↔ ACC-02 / DD-F030 §2.9 | 3 chế độ 2 transaction hay 1 transaction rồi upload. | đã sửa thiết kế (→ PREMISE S-33) |
| E09-g3 | ADR-007 §6 ↔ TBL-accounting_export_lines / FN | ADR còn ghi thuế 10%, gộp người × ngày. | đã sửa thiết kế (→ PREMISE S-34) |
| E09-g4 | ADR-009 daily_report_build ↔ FN-LIST | Không có function spec cho job này. | giả định (→ PREMISE G-10) |
| E09-g5 | DD-F028 §1 ↔ E00-14 / ADR-002 | Bucket reports không có trong danh sách hạ tầng. | giả định (→ PREMISE G-11) |
| E09-g6 | JOB-05 bản chụp RPT 06 ↔ thời điểm xuất batch | Bản chụp dựng trước khi batch kế toán xuất nên rpt06 thường rỗng; rpt03 / 09 không theo biz_date. Tạm thời bỏ rpt06 (PREMISE S-49, H-8), chờ khách xác nhận mục đích bản chụp. | tạo issue làm rõ (#336) |
| E09-g7 | RPT-02 ↔ DD-F028 §3 | Danh sách báo cáo bắt buộc biz_date và nguồn RPT 01 khác nhau. | đã sửa thiết kế (→ PREMISE S-35) |
| E09-g8 | SCREEN-LIST SCR-032 ↔ RPT-01 | Screen list 3 vai trò, API 7 vai trò. | đã sửa thiết kế (→ PREMISE S-36) |
| E09-g9 | OQ-25 (dựng lại báo cáo sau mở / khóa lại) | Chỉ dựng lại ở slot 10:00 hôm sau; khách có thể cần ngay. | để mở — #245 (E09-07) làm theo DD (slot kế tiếp); nếu khách cần ngay thì thêm nút / API (CR nhỏ). |
| E10-g1 | AUD-01 bước 6 ↔ FN audit_chain_verify | AUD-01 gọi chế độ kiểm theo dải mà FN không có. | đã sửa thiết kế (→ PREMISE S-37) |
| E10-g2 | DD-F031 §3.3 ↔ TBL-audit_log_archives | DD chia partNN, bảng chỉ lưu 1 tệp / tháng. | đã sửa thiết kế (→ PREMISE S-38) |
| E10-g3 | FN audit_chain_verify ↔ TBL-audit_log_archives (verified_at) | Băm lại tệp Storage cần endpoint job không có trong API list. Tạm thời không làm JOB-08 ở baseline (PREMISE H-12), chờ xác nhận yêu cầu neo ngoài DB. | tạo issue làm rõ (#337) |
| E10-g4 | ADR-008 Decision 4 / DD-F031 §2.7 | Neo last_row_hash gửi ROLE-011 nhưng không có báo cáo / API / thông báo nào làm. | tạo issue làm rõ (#338) |
| E10-g5 | SCR-034 ↔ API-LIST AUD-03 | Màn còn ghi API trạng thái chuỗi chưa có. | đã sửa thiết kế (→ PREMISE S-39) |
| E10-g6 | SCR-034 C-6 / DD-F031 §1.6 | Không có bảng tổng mã action có nhãn tiếng Nhật. | giả định (→ PREMISE G-12) |
| E10-g7 | FN-LIST No.2 ↔ DD-F031 §1.7 / DD-F035 §3.3 | ATT-03 ghi audit bằng 2 cách khác nhau. | đã sửa thiết kế (→ PREMISE S-40) |
| E11-g1 | FN ops_watchdog A-9 ↔ DD-F034 §2 / SCR-037 | Người nhận A-9 khác nhau. | đã sửa thiết kế (→ PREMISE S-41) |
| E11-g2 | FN sync_resolve ↔ TBL-sync_operations CHECK | CHECK cấm 照合済 có result_entity_id mà 再登録 cần. | đã sửa thiết kế (→ PREMISE S-42) |
| E11-g3 | DD-F007 / DD-F016 ↔ FN create_lot / record_delivery | Chiều gọi sync_apply_operation (trùng E03-g2). | đã sửa thiết kế (→ PREMISE S-43) |
| E11-g4 | ADR-009 sync_operations_purge, attachment_temp_purge ↔ FN-LIST | 2 job không có function spec. | giả định (→ PREMISE G-13) |
| E11-g5 | DD-F035 §6.3 ↔ ops_watchdog / nfr-design §2 | Cảnh báo khôi phục quá hạn không có luật trong A-1〜A-12. | đã sửa thiết kế (→ PREMISE S-44) |
| E11-g6 | DD-F033 §3.4 ↔ CHECK | Thông báo lần giao bị đảo do xung đột chưa có event type. | đã sửa thiết kế (→ PREMISE S-45) |
| E11-g7 | ADR-002 / DD-F034 §6 ↔ OQ-04 | Runner pg_dump và RPO 1 ngày chưa chốt. | giả định (→ PREMISE G-19) |
| E11-g8 | DD-F035 §5.2 ↔ ADR-002 / E00-14 | Tên và loại lưu trữ lạnh chưa chốt. | giả định (→ PREMISE G-14) |
| E11-g9 | OQ-21 (営業日 của hạn khôi phục) | Lịch chợ hay ngày làm việc văn phòng: khách chưa xác nhận. | để mở — #307 (E11-23) đặt cách tính trong 1 hàm, đổi không ảnh hưởng nơi gọi. |
| E11-g10 | DD-F036 §5 / initial-data §3.5 ↔ FN-LIST | Không hàm / API nào đặt migration_runs = ロールバック済. | giả định (→ PREMISE G-15) |
| E11-g11 | DD-F036 §1.6 ↔ ATT-02 | ATT-02 không nhận tài liệu migration. | tạo issue làm rõ (#339) |
| E11-g12 | initial-data §3.3 ↔ TBL-migration_reconciliations | Chỉ số Σ delivered_qty theo tháng không có cột lưu. | đã sửa thiết kế (→ PREMISE S-46) |
| E11-g13 | QA-010 (định dạng Phụ lục C) | Cột / định dạng 3 file nguồn chưa có, loader chưa chốt mapping. | giả định (→ PREMISE G-18) |
| E11-g14 | OPS-03 ↔ SCR-037 tab ジョブ / state-machines §9, §14 | Số job (13 / 12) và giờ chạy lệch giữa tài liệu. | đã sửa thiết kế (→ PREMISE S-47) |
| E11-g15 | DD-F034 §2〜5 ↔ FN-LIST No.73〜76, 86 | DD ghi 4 hàm vận hành "dự kiến" dù FN đã có. | đã sửa thiết kế (→ PREMISE S-48) |
| E11-g16 | OQ-24 (ngưỡng xuất hàng loạt 30 lần / 10 phút) | Ngưỡng A-7 là giá trị thiết kế, chờ khách. | để mở — #291 (E11-10b) đọc ngưỡng từ cấu hình, khách đổi không cần sửa code. |

## Lịch sử thay đổi

| Ngày | Nội dung | Người |
| --- | --- | --- |
| 2026-11-11 | Tạo bản đầu: nguyên tắc chia task, spec → issue, 39 lá 完納奨励金, 87 chỗ hở | PL |
