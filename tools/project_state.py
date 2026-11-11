"""Shared config + local state for the LAB-5 GitHub Project scripts.

State files (committed, no secrets):
  tools/project-state.json  project id/url + field / option / iteration ids
  tools/issue-map.json      backlog key -> issue number, node id, project item id
"""
import json
from pathlib import Path

from github_api_client import graphql

OWNER = "khoanpm-3814"
REPO = "sakura-market-lab5"
PROJECT_TITLE = "Sakura Market — LAB-5 backlog (Product A)"

ROOT = Path(__file__).resolve().parent.parent
BACKLOG_DIR = ROOT / "backlog-data"
STATE_FILE = ROOT / "tools" / "project-state.json"
MAP_FILE = ROOT / "tools" / "issue-map.json"

# Field names used on the Project board (Vietnamese labels shown to reviewers).
F_STATUS, F_ITER, F_SWP, F_HOURS, F_OWNER, F_KIND = (
    "Status", "Iteration", "SWP", "Giờ ước lượng", "Phụ trách (giả định)", "Loại")


def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_backlog():
    """Return epics (list of dicts) sorted by epic id from backlog-data/E*.json."""
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(BACKLOG_DIR.glob("E*.json"))]


def refresh_fields(state):
    """Re-read field / option / iteration ids from GitHub into state['fields']."""
    q = """query($id:ID!){ node(id:$id){ ... on ProjectV2 { fields(first:50){ nodes{
      ... on ProjectV2FieldCommon { id name dataType }
      ... on ProjectV2SingleSelectField { options { id name } }
      ... on ProjectV2IterationField { configuration { iterations { id title startDate duration }
                                                       completedIterations { id title startDate duration } } } } } } } }"""
    nodes = graphql(q, id=state["project_id"])["node"]["fields"]["nodes"]
    fields = {}
    for n in nodes:
        f = {"id": n["id"], "type": n["dataType"]}
        if "options" in n:
            f["options"] = {o["name"]: o["id"] for o in n["options"]}
        if "configuration" in n:
            its = n["configuration"]["iterations"] + n["configuration"]["completedIterations"]
            f["iterations"] = {i["title"]: i["id"] for i in its}
        fields[n["name"]] = f
    state["fields"] = fields
    save_json(STATE_FILE, state)
    return state


def field_value(state, field_name, value):
    """Translate a human value into a ProjectV2FieldValue input for the named field."""
    field = state["fields"][field_name]
    if field["type"] == "NUMBER":
        return {"number": float(value)}
    if field["type"] == "SINGLE_SELECT":
        return {"singleSelectOptionId": field["options"][value]}
    if field["type"] == "ITERATION":
        return {"iterationId": field["iterations"][value]}
    return {"text": str(value)}


def set_fields_batch(state, triples, chunk=12):
    """Set many (item_id, field_name, value) in aliased GraphQL mutations, `chunk` updates per request."""
    for start in range(0, len(triples), chunk):
        part = triples[start:start + chunk]
        decl, body, vars_ = ["$p:ID!"], [], {"p": state["project_id"]}
        for n, (item_id, name, value) in enumerate(part):
            decl += [f"$i{n}:ID!", f"$f{n}:ID!", f"$v{n}:ProjectV2FieldValue!"]
            vars_.update({f"i{n}": item_id, f"f{n}": state["fields"][name]["id"], f"v{n}": field_value(state, name, value)})
            body.append(f"u{n}: updateProjectV2ItemFieldValue(input:{{projectId:$p,itemId:$i{n},fieldId:$f{n},"
                        f"value:$v{n}}}){{ clientMutationId }}")
        graphql(f"mutation({','.join(decl)}){{ {' '.join(body)} }}", **vars_)


def set_field(state, item_id, field_name, value):
    """Set one Project field on one item. value: number | option name | iteration title | None (clear)."""
    field = state["fields"][field_name]
    if value is None:
        graphql("""mutation($p:ID!,$i:ID!,$f:ID!){ clearProjectV2ItemFieldValue(
                   input:{projectId:$p,itemId:$i,fieldId:$f}){ clientMutationId } }""",
                p=state["project_id"], i=item_id, f=field["id"])
        return
    set_fields_batch(state, [(item_id, field_name, value)])
