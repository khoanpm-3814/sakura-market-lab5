"""Create one clarification issue per spec gap whose proposal is "issue làm rõ" (task-breakdown.md §4).

Each becomes a sub-issue of its epic, label type:clarify, owner TL (PL / BrSE work: no hours, no SWP, no sprint).
Idempotent through tools/clarify-map.json (gap id → issue).
Usage: python tools/create-clarify-issues.py
"""
from github_api_client import graphql, rest
from project_state import (F_KIND, F_OWNER, F_STATUS, MAP_FILE, OWNER, REPO, ROOT, STATE_FILE, load_backlog, load_json,
                           refresh_fields, save_json, set_fields_batch)

CLARIFY_MAP = ROOT / "tools" / "clarify-map.json"
R = f"/repos/{OWNER}/{REPO}"


def main():
    state, imap, cmap = refresh_fields(load_json(STATE_FILE, {})), load_json(MAP_FILE, {}), load_json(CLARIFY_MAP, {})
    try:
        rest("POST", f"{R}/labels", {"name": "type:clarify", "color": "e99695"})
    except RuntimeError as err:
        if "already_exists" not in str(err):
            raise
    for e in load_backlog():
        for i, g in enumerate(e.get("spec_gaps", []), 1):
            gid = f"{e['epic']}-g{i}"
            if not g.get("proposal", "").startswith("issue") or gid in cmap:
                continue
            body = "\n".join([
                f"**Epic:** {e['epic']} — {e['title']} · **Mã chỗ hở:** `{gid}` (task-breakdown.md §4)",
                "**Loại:** làm rõ spec LAB-4 — việc của PL / BrSE, không tính giờ dev, không chấm SWP", "",
                "### Spec", g["spec"], "", "### Chỗ hở / mâu thuẫn", g["gap"], "",
                "### Đề xuất khi break", g.get("note") or "—", "",
                "### Xong khi", "- [ ] Có quyết định (PL hoặc khách) ghi vào PREMISE.md / spec LAB-4",
                "- [ ] Issue dev bị ảnh hưởng đã cập nhật mô tả / tiêu chí"])
            iss = rest("POST", f"{R}/issues", {"title": f"[{gid}] Làm rõ: {g['spec'][:90]}", "body": body,
                                              "labels": ["type:clarify", f"epic:{e['epic']}"]})
            item = graphql("""mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p,contentId:$c}){
                              item { id } } }""", p=state["project_id"], c=iss["node_id"])["addProjectV2ItemById"]["item"]["id"]
            rest("POST", f"{R}/issues/{imap[e['epic']]['number']}/sub_issues", {"sub_issue_id": iss["id"]})
            set_fields_batch(state, [(item, F_KIND, "Issue"), (item, F_STATUS, "Todo"), (item, F_OWNER, "TL")])
            cmap[gid] = {"number": iss["number"], "item_id": item}
            save_json(CLARIFY_MAP, cmap)
            print(f"  #{iss['number']} {gid}")
    print(f"clarify issues: {len(cmap)}")


if __name__ == "__main__":
    main()
