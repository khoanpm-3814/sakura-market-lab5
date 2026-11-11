"""Validate backlog-data/E*.json against the breakdown rules in task-breakdown.md.

Checks: unique keys · leaf hours in bands 2/4/8/12/16 · parents carry no hours · depends_on targets exist ·
every baseline F-ID owned by an epic · 完納奨励金 epic has >= 10 constrained leaves.
Prints a per-epic summary; exit 1 on any error.
"""
import sys

from project_state import load_backlog

BANDS = {2, 4, 8, 12, 16}
BASELINE_F = {f"F-{n:03d}" for n in range(1, 37)} | {"F-041"}


def leaves_and_parents(epic):
    for it in epic["issues"]:
        if it.get("sub_issues"):
            yield it, True
            for sub in it["sub_issues"]:
                yield sub, False
        else:
            yield it, False


def main():
    epics = load_backlog()
    errors, keys, rows = [], {}, []
    for e in epics:
        for it, is_parent in leaves_and_parents(e):
            if it["key"] in keys:
                errors.append(f"duplicate key {it['key']}")
            keys[it["key"]] = it
            if is_parent and it.get("hours"):
                errors.append(f"{it['key']}: parent must not carry hours")
            if not is_parent and it.get("hours") not in BANDS:
                errors.append(f"{it['key']}: leaf hours {it.get('hours')} not in bands {sorted(BANDS)}")
            for field in ("title", "description", "acceptance", "spec_refs", "discipline"):
                if not it.get(field):
                    errors.append(f"{it['key']}: missing {field}")
    for k, it in keys.items():
        errors += [f"{k}: depends_on unknown {d}" for d in it.get("depends_on", []) if d not in keys and d not in
                   {e["epic"] for e in epics}]
    owned = {f for e in epics for f in e.get("f_ids", [])}
    errors += [f"F-ID not owned by any epic: {f}" for f in sorted(BASELINE_F - owned)]
    for e in epics:
        leaves = [it for it, p in leaves_and_parents(e) if not p]
        constrained = [it for it in leaves if it.get("constraint")]
        if e.get("constraint") and len(constrained) < 10:
            errors.append(f"{e['epic']}: only {len(constrained)} constrained leaves (< 10)")
        rows.append((e["epic"], len(e["issues"]), len(leaves), sum(it["hours"] for it in leaves if it.get("hours")),
                     len(constrained), len(e.get("spec_gaps", [])), len(e.get("spec_not_issued", []))))
    print("epic issues leaves hours constrained gaps not_issued")
    for r in rows:
        print(*r)
    print("TOTAL", sum(r[1] for r in rows), sum(r[2] for r in rows), sum(r[3] for r in rows))
    for err in errors:
        print("ERROR", err)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
