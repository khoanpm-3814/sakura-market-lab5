"""Push backlog-data/E*.json to GitHub: labels, epic / issue / sub-issue, sub-issue links, Project items.

Idempotent: keys already in tools/issue-map.json are skipped, so an interrupted run can be resumed.
Usage: python tools/push-backlog-issues.py [--only E07] [--dry-run]
"""
import argparse
import time

from github_api_client import graphql, rest
from project_state import (F_HOURS, F_KIND, F_STATUS, MAP_FILE, OWNER, REPO, STATE_FILE, load_backlog, load_json,
                           save_json, set_fields_batch)

R = f"/repos/{OWNER}/{REPO}"
CONSTRAINT_LABEL = "constraint:完納奨励金"
DOD = ("Code + unit test (happy path, lỗi nghiệp vụ, quyền) pass trên CI · review được duyệt · "
       "tiêu chí chấp nhận kiểm được trên môi trường dev · spec LAB-4 liên quan đã cập nhật nếu có thay đổi")


def ensure_labels(epics):
    labels = {CONSTRAINT_LABEL: "d93f0b", "type:epic": "5319e7", "type:issue": "0e8a16", "type:sub-issue": "c2e0c6"}
    for e in epics:
        labels[f"epic:{e['epic']}"] = "1d76db"
        for it in walk(e):
            labels[f"disc:{it['discipline']}"] = "fbca04"
            labels[f"priority:{it.get('priority', 'must')}"] = "bfdadc"
    for name, color in labels.items():
        try:
            rest("POST", f"{R}/labels", {"name": name, "color": color})
        except RuntimeError as err:
            if "already_exists" not in str(err):
                raise


def walk(epic):
    """Yield every issue and sub-issue of an epic (depth-first)."""
    for it in epic["issues"]:
        yield it
        yield from it.get("sub_issues", [])


def ref(key, imap):
    return f"#{imap[key]['number']} ({key})" if key in imap else f"{key}"


def issue_body(epic, it, imap):
    hours = f"{it['hours']} giờ — {it.get('hours_basis', '')}" if it.get("hours") else "tổng của sub-issue"
    lines = [f"**Epic:** {epic['epic']} — {epic['title']} · **Key:** `{it['key']}`",
             f"**Mảng:** {it['discipline']} · **Ưu tiên:** {it.get('priority', 'must')} · **Giờ ước lượng:** {hours}"]
    if it.get("constraint"):
        lines.append(f"**Ràng buộc đặc thù:** {it['constraint']} (tách riêng, không gộp)")
    lines += ["", "### Mô tả", it["description"], "", "### Tiêu chí chấp nhận"]
    lines += [f"- [ ] {a}" for a in it.get("acceptance", [])]
    lines += ["", "### Spec LAB-4", ", ".join(f"`{s}`" for s in it.get("spec_refs", [])) or "—"]
    if it.get("depends_on"):
        lines += ["", "### Phụ thuộc"] + [f"- {ref(k, imap)}" for k in it["depends_on"]]
    lines += ["", "### Định nghĩa xong", DOD]
    return "\n".join(lines)


def epic_body(epic):
    lines = [f"**Epic {epic['epic']}** · F-ID: {', '.join(epic.get('f_ids', [])) or '— (nền tảng chung)'}", "",
             epic.get("summary", "")]
    if epic.get("constraint"):
        lines += ["", f"**Ràng buộc đặc thù của đề:** {epic['constraint']} — các issue mang label `{CONSTRAINT_LABEL}`."]
    lines += ["", "Issue con: xem mục Sub-issues. SWP của epic = tổng SWP issue lá."]
    return "\n".join(lines)


def existing_issues():
    """Map '[KEY]' title prefix -> issue JSON for issues already on GitHub (adopts orphans of an interrupted run)."""
    out, page = {}, 1
    while True:
        batch = rest("GET", f"{R}/issues?state=all&per_page=100&page={page}")
        for iss in batch or []:
            if iss["title"].startswith("[") and "pull_request" not in iss:
                out[iss["title"][1:iss["title"].index("]")]] = iss
        if not batch or len(batch) < 100:
            return out
        page += 1


def create(key, title, body, labels, kind, hours, state, imap, parent_key=None, existing=None):
    if key in imap:
        return imap[key]
    iss = (existing or {}).get(key) or rest("POST", f"{R}/issues", {"title": title, "body": body, "labels": labels})
    rec = {"number": iss["number"], "id": iss["id"], "node_id": iss["node_id"], "kind": kind, "hours": hours}
    item = graphql("""mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p,contentId:$c}){ item { id } } }""",
                   p=state["project_id"], c=iss["node_id"])
    rec["item_id"] = item["addProjectV2ItemById"]["item"]["id"]
    if parent_key:
        try:
            rest("POST", f"{R}/issues/{imap[parent_key]['number']}/sub_issues", {"sub_issue_id": iss["id"]})
        except RuntimeError as err:  # already linked when adopting an orphan
            if "already" not in str(err).lower() and "duplicate" not in str(err).lower():
                raise
        rec["parent"] = parent_key
    # Linked when every dependency line already shows an issue number (dependency created earlier).
    dep_lines = [ln for ln in body.split("### Phụ thuộc")[-1].split("###")[0].splitlines() if ln.startswith("- ")] \
        if "### Phụ thuộc" in body else []
    rec["deps_linked"] = all(ln.startswith("- #") for ln in dep_lines)
    imap[key] = rec
    save_json(MAP_FILE, imap)
    print(f"  #{iss['number']} {key} {title[:60]}")
    time.sleep(0.3)  # stay under GitHub content-creation secondary limits
    return rec


def apply_initial_fields(state, imap):
    """Batch-set Loại / Status / Giờ for items not yet initialised (fields_done flag in issue-map)."""
    todo = [(k, r) for k, r in imap.items() if not r.get("fields_done")]
    for start in range(0, len(todo), 4):  # 4 items ≈ 12 updates per request; saved per group for resume
        group, triples = todo[start:start + 4], []
        for _, r in group:
            triples += [(r["item_id"], F_KIND, r["kind"]), (r["item_id"], F_STATUS, "Todo")]
            if r.get("hours"):
                triples.append((r["item_id"], F_HOURS, r["hours"]))
        set_fields_batch(state, triples, chunk=12)
        for k, _ in group:
            imap[k]["fields_done"] = True
        save_json(MAP_FILE, imap)
    print(f"fields set for {len(todo)} items")


def labels_for(epic, it, kind):
    out = [f"epic:{epic['epic']}", f"type:{kind.lower()}", f"disc:{it['discipline']}", f"priority:{it.get('priority', 'must')}"]
    return out + ([CONSTRAINT_LABEL] if it.get("constraint") else [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    epics = [e for e in load_backlog() if not a.only or e["epic"] == a.only]
    if a.dry_run:
        for e in epics:
            leaves = [i for i in walk(e) if not i.get("sub_issues")]
            print(e["epic"], "issues", len(list(walk(e))), "leaf", len(leaves), "hours", sum(i.get("hours") or 0 for i in leaves))
        return
    state, imap = load_json(STATE_FILE, {}), load_json(MAP_FILE, {})
    ensure_labels(epics)
    ex = {k: v for k, v in existing_issues().items() if k not in imap}
    for e in epics:
        elabels = ["type:epic", f"epic:{e['epic']}"] + ([CONSTRAINT_LABEL] if e.get("constraint") else [])
        create(e["epic"], f"[{e['epic']}] {e['title']}", epic_body(e), elabels, "Epic", None, state, imap, existing=ex)
        for it in e["issues"]:
            create(it["key"], f"[{it['key']}] {it['title']}", issue_body(e, it, imap), labels_for(e, it, "Issue"),
                   "Issue", None if it.get("sub_issues") else it.get("hours"), state, imap, parent_key=e["epic"],
                   existing=ex)
            for sub in it.get("sub_issues", []):
                create(sub["key"], f"[{sub['key']}] {sub['title']}", issue_body(e, sub, imap),
                       labels_for(e, sub, "Sub-issue"), "Sub-issue", sub.get("hours"), state, imap,
                       parent_key=it["key"], existing=ex)
    apply_initial_fields(state, imap)
    # Second pass: rewrite bodies whose dependencies were created after them.
    for e in epics:
        for it in walk(e):
            if imap.get(it["key"], {}).get("deps_linked") is False:
                rest("PATCH", f"{R}/issues/{imap[it['key']]['number']}", {"body": issue_body(e, it, imap)})
                imap[it["key"]]["deps_linked"] = True
                save_json(MAP_FILE, imap)


if __name__ == "__main__":
    main()
