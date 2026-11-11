"""Deterministic simulation of Sprint 1 (2027-02-01 → 2027-02-12, 10 working days) for the sample progress report.

Model: each assumed owner works their Sprint 1 leaves in plan order (dependencies first) at 6 focus h/day
(TL 3 h/day). Actual hours = estimate × multiplier; EVENTS below inject the deviations explained in
progress-report.md. An issue is Done on the day its actual hours are used up; unfinished issues end as
In Review (≥ 80 % of actual hours spent) or In Progress / Todo.
Outputs: sprint-plan/sprint-1-simulation.json, sprint-plan/sprint-1-status.json (field values for the Project),
progress/burndown-sprint-1.svg
"""
import datetime as dt
import json

from project_state import F_ITER, F_OWNER, F_STATUS, ROOT, load_backlog

DAYS = [dt.date(2027, 2, 1) + dt.timedelta(days=d) for d in range(12) if (dt.date(2027, 2, 1) + dt.timedelta(days=d)).weekday() < 5]
RATE = {"TL": 3}
DEFAULT_RATE = 6
# key: (multiplier on estimate, blocked working days before work can continue, note)
EVENTS = {
    "E00-14": (1.0, 3, "Chờ khách duyệt tạo org Supabase Pro / Vercel ở Tokyo (thanh toán) — mất 3 ngày"),
    "E00-02d": (1.5, 0, "Migration lô / giao dịch / せり: sửa lock order và cột theo PREMISE H-1 / H-4 → vượt 6h"),
    "E00-09": (1.5, 0, "Spec thiếu bảng lưu Idempotency-Key (PREMISE S-01) → thiết kế thêm bảng, vượt 4h"),
    "E10-11": (1.0, 99, "Kiểm phủ audit cho mọi hàm ghi: phần lớn hàm nghiệp vụ chưa có → không thể xong trong sprint"),
}


def sprint1_leaves():
    plan = json.loads((ROOT / "sprint-plan" / "sprint-assignments.json").read_text(encoding="utf-8"))
    swp = json.loads((ROOT / "generated" / "swp-by-key.json").read_text(encoding="utf-8"))
    order = []
    for e in load_backlog():
        for it in e["issues"]:
            for lf in it.get("sub_issues") or [it]:
                if plan.get(lf["key"], {}).get(F_ITER) == "Sprint 1":
                    order.append({"key": lf["key"], "title": lf["title"], "hours": lf["hours"], "swp": swp[lf["key"]],
                                  "owner": plan[lf["key"]][F_OWNER], "epic": e["epic"], "parent": it["key"]})
    return order


def simulate(items):
    """Sequential queue per owner: cumulative hours / daily rate → finish day; a block delays finish by N days."""
    done_day, spent, cursor = {}, {}, {}
    for it in items:
        rate = RATE.get(it["owner"], DEFAULT_RATE)
        mult, blocked, _ = EVENTS.get(it["key"], (1.0, 0, ""))
        if blocked >= len(DAYS):  # parked after 2h investigation; owner moves on
            spent[it["key"]] = 2.0
            cursor[it["owner"]] = cursor.get(it["owner"], 0) + 2
            continue
        need = it["hours"] * mult
        before = cursor.get(it["owner"], 0)
        cursor[it["owner"]] = before + need
        finish = -(-cursor[it["owner"]] // rate) - 1 + blocked  # ceil(h / rate) - 1, shifted by block days
        capacity = rate * (len(DAYS) - blocked)
        spent[it["key"]] = max(0.0, min(need, capacity - before))
        if finish <= len(DAYS) - 1:
            done_day[it["key"]] = int(finish)
    return done_day, spent


def status_of(it, done_day, spent):
    if it["key"] in done_day:
        return "Done"
    mult = EVENTS.get(it["key"], (1.0, 0, ""))[0]
    ratio = spent.get(it["key"], 0) / (it["hours"] * mult)
    return "In Review" if ratio >= 0.8 else ("In Progress" if ratio > 0 else "Todo")


def burndown_svg(series, ideal, path):
    w, h, pad = 640, 320, 48
    top = max(ideal[0], max(series))
    x = lambda i: pad + i * (w - 2 * pad) / (len(ideal) - 1)
    y = lambda v: h - pad - v * (h - 2 * pad) / top
    pts = lambda vals: " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    labels = "".join(f'<text x="{x(i):.1f}" y="{h - pad + 18}" font-size="10" text-anchor="middle">{d}</text>'
                     for i, d in enumerate(["start"] + [d.strftime("%m-%d") for d in DAYS]))
    ticks = "".join(f'<text x="{pad - 6}" y="{y(v) + 4:.1f}" font-size="10" text-anchor="end">{v:.0f}</text>'
                    for v in (0, top / 2, top))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="sans-serif">'
           f'<rect width="{w}" height="{h}" fill="#ffffff"/>'
           f'<line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="#888"/>'
           f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h - pad}" stroke="#888"/>{labels}{ticks}'
           f'<polyline fill="none" stroke="#9aa5b1" stroke-dasharray="6 4" stroke-width="2" points="{pts(ideal)}"/>'
           f'<polyline fill="none" stroke="#d1495b" stroke-width="2.5" points="{pts(series)}"/>'
           f'<text x="{pad}" y="24" font-size="13" font-weight="bold">Sprint 1 burndown (SWP còn lại) — 2027-02-01〜02-12</text>'
           f'<text x="{w - pad}" y="24" font-size="11" text-anchor="end" fill="#d1495b">— thực tế</text>'
           f'<text x="{w - pad}" y="38" font-size="11" text-anchor="end" fill="#9aa5b1">- - lý tưởng</text></svg>')
    path.parent.mkdir(exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def main():
    items = sprint1_leaves()
    done_day, spent = simulate(items)
    total = sum(i["swp"] for i in items)
    remaining = [total] + [total - sum(i["swp"] for i in items if done_day.get(i["key"], 99) <= d) for d in range(len(DAYS))]
    ideal = [total - total * d / len(DAYS) for d in range(len(DAYS) + 1)]
    statuses = {i["key"]: status_of(i, done_day, spent) for i in items}
    sim = {"days": [d.isoformat() for d in DAYS], "committed_swp": total, "committed_hours": sum(i["hours"] for i in items),
           "remaining_swp": remaining, "ideal_swp": [round(v, 1) for v in ideal],
           "items": [i | {"status": statuses[i["key"]], "done_day": DAYS[done_day[i["key"]]].isoformat() if i["key"] in done_day else None,
                          "spent_hours": round(spent.get(i["key"], 0), 1), "event": EVENTS.get(i["key"], (0, 0, ""))[2]}
                     for i in items]}
    (ROOT / "sprint-plan" / "sprint-1-simulation.json").write_text(json.dumps(sim, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    field_values = {k: {F_STATUS: s} for k, s in statuses.items()}
    for parent in {i["parent"] for i in items if i["parent"] != i["key"]}:
        kids = [statuses[i["key"]] for i in items if i["parent"] == parent]
        field_values[parent] = {F_STATUS: "Done" if all(s == "Done" for s in kids) else "In Progress"}
    for epic in {i["epic"] for i in items}:
        field_values[epic] = {F_STATUS: "In Progress"}
    (ROOT / "sprint-plan" / "sprint-1-status.json").write_text(json.dumps(field_values, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    burndown_svg(remaining, ideal, ROOT / "progress" / "burndown-sprint-1.svg")
    counts = {}
    for i in items:
        c = counts.setdefault(statuses[i["key"]], [0, 0, 0])
        c[0] += 1; c[1] += i["swp"]; c[2] += i["hours"]
    print("committed", total, "SWP", sim["committed_hours"], "h; remaining by day", remaining)
    print({k: v for k, v in counts.items()})


if __name__ == "__main__":
    main()
