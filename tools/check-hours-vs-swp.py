"""Consistency check between direct hour estimates and reviewed SWP (rule in estimate.md §3).

Flags leaves whose hours/SWP ratio is outside [median / 2, median × 2] of their discipline.
Usage: python tools/check-hours-vs-swp.py  → prints medians and outliers; writes generated/hours-vs-swp.json
"""
import json
import statistics

from project_state import ROOT, load_backlog

SWP_FILE = ROOT / "generated" / "swp-by-key.json"
OUT = ROOT / "generated" / "hours-vs-swp.json"


def main():
    swp = json.loads(SWP_FILE.read_text(encoding="utf-8"))
    rows = []
    for e in load_backlog():
        for it in e["issues"]:
            for lf in it.get("sub_issues") or [it]:
                rows.append({"key": lf["key"], "disc": lf["discipline"], "hours": lf["hours"], "swp": swp[lf["key"]],
                             "ratio": lf["hours"] / swp[lf["key"]], "title": lf["title"]})
    medians = {d: statistics.median(r["ratio"] for r in rows if r["disc"] == d) for d in {r["disc"] for r in rows}}
    overall = statistics.median(r["ratio"] for r in rows)
    out = [r | {"median": medians[r["disc"]]} for r in rows
           if not medians[r["disc"]] / 2 <= r["ratio"] <= medians[r["disc"]] * 2]
    OUT.write_text(json.dumps({"overall_median": overall, "medians": medians, "outliers": out}, ensure_ascii=False,
                              indent=1) + "\n", encoding="utf-8")
    print("overall h/SWP median", round(overall, 2), {d: round(m, 2) for d, m in sorted(medians.items())})
    print("total hours", sum(r["hours"] for r in rows), "total SWP", sum(r["swp"] for r in rows))
    for r in out:
        print(f"OUTLIER {r['key']} {r['disc']} {r['hours']}h / {r['swp']} SWP = {r['ratio']:.2f} "
              f"(median {r['median']:.2f}) {r['title'][:60]}")


if __name__ == "__main__":
    main()
