"""Generate the Markdown tables used by README / PREMISE / task-breakdown / estimate from backlog-data + issue-map.

Writes generated/report-tables.md (one H2 per table) so the hand-written docs can paste or link stable numbers.
Gap handling ids: sửa thiết kế → S-nn (PREMISE §1) · giả định → G-nn (PREMISE §2) · issue làm rõ → #number
(from tools/clarify-map.json once created) · để mở → reason kept.
Usage: python tools/build-report-tables.py
"""
import re

from project_state import MAP_FILE, ROOT, load_backlog, load_json

CLARIFY_MAP = ROOT / "tools" / "clarify-map.json"
SWP_FILE = ROOT / "generated" / "swp-by-key.json"
OUT = ROOT / "generated" / "report-tables.md"


def num(imap, key):
    return f"#{imap[key]['number']}" if key in imap else key


def leaves(epic):
    for it in epic["issues"]:
        yield from (it.get("sub_issues") or [it])


def esc(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


SPEC_TOKEN = re.compile(r"(FN-[\w-]+|DD-F\d{3}|SCR-\d{3}|TBL-[a-z_]+|ADR-\d{3}|\b[A-Z]{2,4}-\d{2}\b)")


def norm(token):
    return token.lower().replace("_", "-")


def affected(text, epics, imap, limit=5):
    """Issues whose spec_refs share a spec id with the gap text (leaf issues first, capped)."""
    toks = {norm(t) for t in SPEC_TOKEN.findall(text)}
    hits = []
    for e in epics:
        for lf in leaves(e):
            refs = {norm(r) for r in lf.get("spec_refs", [])}
            if any(r == t or r.startswith(t) or t.startswith(r) for r in refs for t in toks):
                hits.append(num(imap, lf["key"]))
    return ", ".join(hits[:limit]) + (f" (+{len(hits) - limit})" if len(hits) > limit else "") or "—"


def main():
    epics, imap = load_backlog(), load_json(MAP_FILE, {})
    clar, swp = load_json(CLARIFY_MAP, {}), load_json(SWP_FILE, {})
    md = ["# Bảng sinh tự động (tools/build-report-tables.py)", ""]

    md += ["## spec-to-epic", "", "| Spec (LAB-4) | Epic trên Project | Ghi chú |", "| --- | --- | --- |"]
    for e in epics:
        note = f"Ràng buộc đặc thù: {e['constraint']}" if e.get("constraint") else ""
        md.append(f"| {', '.join(e.get('f_ids', [])) or 'ADR-001〜010, common-spec, TBL nền'} | "
                  f"{num(imap, e['epic'])} — [{e['epic']}] {esc(e['title'])} | {note} |")

    md += ["", "## spec-to-issue", "", "| Spec | Epic | Issue / sub-issue | Phần spec chưa thành issue và vì sao |",
           "| --- | --- | --- | --- |"]
    for e in epics:
        issues = []
        for it in e["issues"]:
            subs = it.get("sub_issues") or []
            issues.append(num(imap, it["key"]) + (f" ({', '.join(num(imap, s['key']) for s in subs)})" if subs else ""))
        gaps = "; ".join(f"{esc(x['spec'])}: {esc(x['reason'])}" for x in e.get("spec_not_issued", [])) or "—"
        md.append(f"| {', '.join(e.get('f_ids', [])) or 'Nền tảng'} | {e['epic']} | {', '.join(issues)} | {gaps} |")

    md += ["", "## constraint-items", "", "| Ràng buộc | Issue | Nội dung | Giờ | SWP |", "| --- | --- | --- | --- | --- |"]
    for e in epics:
        for lf in leaves(e):
            if lf.get("constraint"):
                md.append(f"| {lf['constraint']} | {num(imap, lf['key'])} `{lf['key']}` | {esc(lf['title'])} | "
                          f"{lf['hours']} | {swp.get(lf['key'], '')} |")

    gaps_md = ["", "## spec-gaps", "", "| # | Spec | Chỗ hở / mâu thuẫn | Xử lý | Ghi chú |",
               "| --- | --- | --- | --- | --- |"]
    prem_s = ["", "## premise-spec-changes", "", "| ID | Spec (mã / file) | Thêm / Bỏ / Sửa | Trước → sau | Vì sao | Issue bị ảnh hưởng |",
              "| --- | --- | --- | --- | --- | --- |"]
    prem_g = ["", "## premise-assumptions", "", "| ID | Giả định | Chỗ spec / RFP để ngỏ | Ảnh hưởng tới issue / estimate |",
              "| --- | --- | --- | --- |"]
    counters = {"S": 0, "G": 0}
    for e in epics:
        for i, g in enumerate(e.get("spec_gaps", []), 1):
            p, gid, note = g.get("proposal", ""), f"{e['epic']}-g{i}", esc(g.get("note", ""))
            hit = affected(g["spec"] + " " + g["gap"], epics, imap)
            if p.startswith("sửa"):
                counters["S"] += 1
                sid = f"S-{counters['S']:02d}"
                act = f"đã sửa thiết kế (PREMISE {sid})"
                prem_s.append(f"| {sid} | {esc(g['spec'])} | Sửa | {esc(g['gap'])} → {note} | "
                              f"Chỗ hở phát hiện khi break {e['epic']} ({gid}) | {hit} |")
            elif p.startswith("giả định"):
                counters["G"] += 1
                gid_p = f"G-{counters['G']:02d}"
                act = f"giả định (PREMISE {gid_p})"
                prem_g.append(f"| {gid_p} | {note} | {esc(g['spec'])}: {esc(g['gap'])} | {hit} |")
            elif p.startswith("issue"):
                act = f"tạo issue làm rõ ({num(clar, gid) if gid in clar else 'chưa tạo'})"
            else:
                act = f"để mở — {note}"
            gaps_md.append(f"| {gid} | {esc(g['spec'])} | {esc(g['gap'])} | {act} | {note} |")
    md += gaps_md + prem_s + prem_g

    md += ["", "## epic-totals", "", "| Epic | Số issue (lá) | Tổng SWP | Tổng giờ | Ghi chú |", "| --- | --- | --- | --- | --- |"]
    tot = [0, 0, 0]
    for e in epics:
        lv = list(leaves(e))
        s = sum(swp.get(lf["key"], 0) for lf in lv)
        h = sum(lf["hours"] for lf in lv)
        tot = [tot[0] + len(lv), tot[1] + s, tot[2] + h]
        md.append(f"| {e['epic']} {esc(e['title'])} | {len(lv)} | {s or ''} | {h} | |")
    md.append(f"| **Tổng** | **{tot[0]}** | **{tot[1] or ''}** | **{tot[2]}** | |")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  S={counters['S']} G={counters['G']}")


if __name__ == "__main__":
    main()
