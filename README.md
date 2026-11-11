# Sakura Market — LAB-5: break task, GitHub Project và báo cáo tiến độ

**Dự án:** 桜水産市場 (sàn đấu giá / 相対取引 thủy sản) · **Mã học viên:** KhoaNPM (GitHub khoanpm-3814) · **Đề:** Product A

## 1. Tổng quan

- Backlog được break từ **bộ spec LAB-4 nộp ngày 2026-11-10** (Sun QMS spec standard: 37 màn, 122 API, 88 function spec, 22 detail design, 46 bảng, ADR-001〜010).
- **PREMISE.md có thay đổi** so với LAB-4: 50 dòng spec thêm / bỏ / sửa (S-01〜S-50), 19 giả định bổ sung (G-01〜G-19), 12 hướng chốt về spec (H-1〜H-12) và 3 về kế hoạch (P-1〜P-3). Nguồn là 87 chỗ hở hoặc mâu thuẫn phát hiện khi break.
- **12 epic** (E00 nền tảng chung + E01〜E11 theo nhóm chức năng), 324 issue dev (12 epic, 39 issue cha, 273 issue lá) và 15 issue làm rõ spec. Tổng **2,122 giờ / 1,247 SWP**.
- Ràng buộc đặc thù của đề: **完納奨励金** tách thành 39 issue lá riêng trong E07, label `constraint:完納奨励金` (xem [task-breakdown.md §3](task-breakdown.md)).
- Sprint giả lập đã chạy: **Sprint 1 (2027-02-01〜2027-02-12)**. Cam kết 134 SWP, xong 112 SWP (84 %), báo cáo ở [progress-report.md](progress-report.md).

## 2. Link

| Mục | Link |
|---|---|
| Repo (public) | https://github.com/khoanpm-3814/sakura-market-lab5 |
| GitHub Project (public) | https://github.com/users/khoanpm-3814/projects/1 |
| Báo cáo HTML của skill chấm SWP (trong repo) | [reports/estimate-swp-sakura-market-lab5-20261111.html](reports/estimate-swp-sakura-market-lab5-20261111.html) |
| Bản xem trực tiếp qua GitHub Pages | https://khoanpm-3814.github.io/sakura-market-lab5/reports/estimate-swp-sakura-market-lab5-20261111.html |

Kiểm tra truy cập không đăng nhập (2026-11-11): repo, Project và trang báo cáo đều trả HTTP 200 khi gọi không kèm token. Học viên đã mở thử cả 3 link bằng cửa sổ ẩn danh (2026-11-11): đều xem được, không cần đăng nhập.

Trên Project, các field dùng để chấm: **Status** (Todo / In Progress / In Review / Done), **Iteration** (Sprint 1〜10), **Phụ trách (giả định)** (TL / BE-1 / BE-2 / FE-1 / FE-2 / QA-1), **SWP** (điểm đã qua review của skill), **Giờ ước lượng**, **Loại** (Epic / Issue / Sub-issue). Quan hệ epic → issue → sub-issue dùng sub-issue gốc của GitHub.

## 3. Cấu trúc repo

| File / thư mục | Nội dung |
|---|---|
| `README.md` | File này |
| `PREMISE.md` | Backlog khác spec LAB-4 ở đâu: spec sửa, giả định, hướng đã chốt |
| `task-breakdown.md` | Nguyên tắc chia task, spec → issue, hạng mục 完納奨励金, chỗ hở spec |
| `estimate.md` | Issue mẫu skill chấm, cách quy ra giờ, tổng theo epic, so với estimate LAB-1 |
| `progress-report.md` | Báo cáo tiến độ Sprint 1 (trạng thái, burndown, rủi ro trễ) gửi khách |
| `AI-report.md` | Skill / prompt đã dùng, cách review output AI, điểm đặc biệt |
| `reports/` | Báo cáo HTML của skill `estimate-swp` (thư mục báo cáo SWP theo đề) |
| `backlog-data/` | Backlog gốc dạng JSON, mỗi epic 1 file (nguồn duy nhất để đẩy lên GitHub và sinh bảng) |
| `tools/` | Script Python: tạo Project, đẩy issue / sub-issue, ghi field, kiểm backlog, xếp sprint, giả lập Sprint 1, sinh bảng báo cáo; `issue-map.json` (key → số issue) |
| `generated/` | Dữ liệu sinh tự động: bảng báo cáo, SWP theo key, đối chiếu giờ / SWP, giá trị field Project |
| `sprint-plan/` | Kế hoạch sprint (Iteration + người phụ trách) và kết quả giả lập Sprint 1 |
| `progress/` | Ảnh burndown Sprint 1 (SVG) |
| `.gitignore` | Bỏ cache Python và file môi trường |

Không có thư mục `skills/`: bài này dùng skill có sẵn của Takumi kit (`estimate-swp`, `confidence`), không viết hoặc chỉnh skill. Phần tự động hóa riêng nằm ở `tools/`.

## 4. Spec → epic

| Spec (LAB-4) | Epic trên Project | Ghi chú |
|---|---|---|
| ADR-001〜010, common-spec, bảng nền (job_runs, attachments, audit_logs…) | #1 — [E00] Nền tảng chung | Gồm chuyển region sang Tokyo (tech debt của prototype) |
| F-001, F-002 | #41 — [E01] Đăng nhập & phân quyền | |
| F-003〜F-006 | #58 — [E02] Người tham gia & tư cách | Tư cách theo kỳ hiệu lực (ADR-010) |
| F-007〜F-010 | #84 — [E03] Lô hàng | Lô chỉ công khai sau 下見済 (A-08) |
| F-011〜F-014 | #99 — [E04] Giao dịch 相対 / せり | Lock order ADR-003, Idempotency-Key TRD-03 |
| F-015〜F-018 | #123 — [E05] Giao hàng | Offline replay, 1 dòng 精算 mỗi lần giao |
| F-019〜F-022 | #143 — [E06] Đối soát, khóa ngày, điều chỉnh, tranh chấp | Sửa sau 確定 bằng reverse / delta |
| F-023, F-024, F-025, F-041 | #169 — [E07] 完納奨励金 & 入金 | **Ràng buộc đặc thù của đề: 完納奨励金** — tách 39 issue lá theo biến nghiệp vụ |
| F-026, F-027 | #217 — [E08] Thông báo | |
| F-028〜F-030 | #229 — [E09] Báo cáo & xuất CSV kế toán | |
| F-031, F-032 | #260 — [E10] Audit | Chuỗi hash, append-only |
| F-033〜F-036 | #275 — [E11] Offline, giám sát vận hành, lưu trữ chứng từ, migration | Loader migration chờ QA-010 |
| PREMISE (chỗ hở cần khách / PL quyết) | 15 issue `type:clarify` #325〜#339 (sub-issue của epic tương ứng) | Không tính giờ, không chấm SWP |

## Lịch sử thay đổi

| Ngày | Nội dung | Người |
|---|---|---|
| 2026-11-11 | Tạo mới | khoanpm-3814 (PL) |
