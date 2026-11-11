"""Build Project field values for SWP (leaf = reviewed score from the estimate-swp report; parent / epic = sum of
children) merged with the sprint plan (Iteration, Phụ trách). Output feeds tools/apply-project-fields.py.

Usage: python tools/build-swp-field-values.py  → generated/project-field-values.json
"""
import json

from project_state import F_SWP, ROOT, load_backlog

SWP_FILE = ROOT / "generated" / "swp-by-key.json"
PLAN_FILE = ROOT / "sprint-plan" / "sprint-assignments.json"
OUT = ROOT / "generated" / "project-field-values.json"


def main():
    swp = json.loads(SWP_FILE.read_text(encoding="utf-8"))
    plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    values = {k: dict(v) for k, v in plan.items()}
    missing = []
    for e in load_backlog():
        epic_total = 0
        for it in e["issues"]:
            leaves = it.get("sub_issues") or [it]
            for lf in leaves:
                if lf["key"] not in swp:
                    missing.append(lf["key"])
                    continue
                values.setdefault(lf["key"], {})[F_SWP] = swp[lf["key"]]
            total = sum(swp.get(lf["key"], 0) for lf in leaves)
            if it.get("sub_issues"):
                values.setdefault(it["key"], {})[F_SWP] = total
            epic_total += total
        values.setdefault(e["epic"], {})[F_SWP] = epic_total
    OUT.write_text(json.dumps(values, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"items={len(values)} missing_swp={missing}")


if __name__ == "__main__":
    main()
