"""Greedy sprint planning for backlog leaves: priority → dependencies → capacity per (assumed) owner.

Rules (documented in progress-report.md / task-breakdown.md):
  - owner by discipline: BE → BE-1|BE-2|FE-2 (full-stack), DB → BE-1|BE-2|TL, FE → FE-1|FE-2, QA → QA-1,
    INFRA → TL (least-loaded wins)
  - capacity per 2-week sprint: 60 focus hours per member (10 days × 6h), TL 30h (half is review / lead work)
  - a leaf is planned only after all its dependency leaves are planned in the same or an earlier sprint
    (dependency on a parent/epic = all of that parent's leaves)
  - order inside the ready set: priority (must > should > could), then epic order, then key
Output: sprint-plan/sprint-assignments.json  {key: {"Iteration": "Sprint N", "Phụ trách (giả định)": owner}}
"""
import json

from project_state import F_ITER, F_OWNER, ROOT, load_backlog

CAPACITY = {"TL": 30, "BE-1": 60, "BE-2": 60, "FE-1": 60, "FE-2": 60, "QA-1": 60}
POOL = {"BE": ["BE-1", "BE-2", "FE-2"], "DB": ["BE-1", "BE-2", "TL"], "FE": ["FE-1", "FE-2"], "QA": ["QA-1"], "INFRA": ["TL"]}
PRIORITY = {"must": 0, "should": 1, "could": 2}
OUT = ROOT / "sprint-plan" / "sprint-assignments.json"


def collect(epics):
    """Return leaves (ordered) and a map container-key -> leaf keys."""
    leaves, groups = [], {}
    for ei, e in enumerate(epics):
        groups[e["epic"]] = []
        for it in e["issues"]:
            subs = it.get("sub_issues") or []
            kids = subs if subs else [it]
            if subs:
                groups[it["key"]] = [s["key"] for s in subs]
            for leaf in kids:
                deps = list(leaf.get("depends_on", [])) + (list(it.get("depends_on", [])) if subs else [])
                leaves.append({**leaf, "epic_order": ei, "deps": deps,
                               "priority": leaf.get("priority") or it.get("priority", "must")})
                groups[e["epic"]].append(leaf["key"])
    return leaves, groups


def plan(epics, max_sprints=12):
    leaves, groups = collect(epics)
    expand = lambda d: groups.get(d, [d])
    placed, out, sprint = {}, {}, 1
    while len(placed) < len(leaves) and sprint <= max_sprints:
        load = dict.fromkeys(CAPACITY, 0)
        progress = True
        while progress:
            progress = False
            ready = [lf for lf in leaves if lf["key"] not in placed and all(
                placed.get(k, 99) <= sprint for d in lf["deps"] for k in expand(d) if k != lf["key"])]
            ready.sort(key=lambda lf: (PRIORITY.get(lf["priority"], 1), lf["epic_order"], lf["key"]))
            for lf in ready:
                owner = min(POOL.get(lf["discipline"], ["BE-1", "BE-2"]), key=lambda o: load[o])
                if load[owner] + lf["hours"] <= CAPACITY[owner]:
                    load[owner] += lf["hours"]
                    placed[lf["key"]] = sprint
                    out[lf["key"]] = {F_ITER: f"Sprint {sprint}", F_OWNER: owner}
                    progress = True
        sprint += 1
    unplaced = [lf["key"] for lf in leaves if lf["key"] not in placed]
    return out, unplaced


def main():
    epics = load_backlog()
    out, unplaced = plan(epics)
    for e in epics:  # containers: owner TL for epics, owner of first child for parent issues; no iteration
        out[e["epic"]] = {F_OWNER: "TL"}
        for it in e["issues"]:
            if it.get("sub_issues"):
                out[it["key"]] = {F_OWNER: out[it["sub_issues"][0]["key"]][F_OWNER]}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    per = {}
    hours = {lf["key"]: lf["hours"] for lf in collect(epics)[0]}
    for k, v in out.items():
        if F_ITER in v:
            per.setdefault(v[F_ITER], [0, 0])
            per[v[F_ITER]][0] += 1
            per[v[F_ITER]][1] += hours[k]
    for s in sorted(per, key=lambda s: int(s.split()[1])):
        print(s, "leaves", per[s][0], "hours", per[s][1])
    print("unplaced", unplaced)


if __name__ == "__main__":
    main()

