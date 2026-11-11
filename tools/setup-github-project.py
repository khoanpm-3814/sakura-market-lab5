"""Create (or reuse) the public GitHub Project for LAB-5 and its custom fields. Idempotent.

Usage: python tools/setup-github-project.py --sprints 10 --start 2027-02-01
"""
import argparse
import datetime as dt

from github_api_client import graphql
from project_state import (F_HOURS, F_ITER, F_KIND, F_OWNER, F_STATUS, F_SWP, OWNER, PROJECT_TITLE, REPO,
                           STATE_FILE, load_json, refresh_fields, save_json)

OWNERS = ["TL", "BE-1", "BE-2", "FE-1", "FE-2", "QA-1"]
KINDS = ["Epic", "Issue", "Sub-issue"]
STATUSES = [("Todo", "GRAY"), ("In Progress", "YELLOW"), ("In Review", "BLUE"), ("Done", "GREEN")]


def options(names, color="GRAY"):
    return [{"name": n, "color": color, "description": ""} for n in names]


def ensure_project(state):
    if state.get("project_id"):
        return state
    ids = graphql("""query($o:String!,$r:String!){ user(login:$o){ id }
                     repository(owner:$o,name:$r){ id } }""", o=OWNER, r=REPO)
    p = graphql("""mutation($o:ID!,$t:String!,$r:ID!){ createProjectV2(input:{ownerId:$o,title:$t,repositoryId:$r}){
                   projectV2 { id number url } } }""",
                o=ids["user"]["id"], t=PROJECT_TITLE, r=ids["repository"]["id"])["createProjectV2"]["projectV2"]
    state.update(project_id=p["id"], number=p["number"], url=p["url"])
    save_json(STATE_FILE, state)
    return state


def ensure_fields(state, sprints, start):
    state = refresh_fields(state)
    have = state["fields"]
    pid = state["project_id"]
    create = """mutation($p:ID!,$n:String!,$t:ProjectV2CustomFieldType!,$o:[ProjectV2SingleSelectFieldOptionInput!],
                $c:ProjectV2IterationFieldConfigurationInput){ createProjectV2Field(input:{projectId:$p,name:$n,
                dataType:$t,singleSelectOptions:$o,iterationConfiguration:$c}){ clientMutationId } }"""
    for name, kind, opts in [(F_SWP, "NUMBER", None), (F_HOURS, "NUMBER", None),
                             (F_OWNER, "SINGLE_SELECT", options(OWNERS)), (F_KIND, "SINGLE_SELECT", options(KINDS))]:
        if name not in have:
            graphql(create, p=pid, n=name, t=kind, o=opts, c=None)
    if F_ITER not in have:
        d0 = dt.date.fromisoformat(start)
        its = [{"title": f"Sprint {i + 1}", "startDate": (d0 + dt.timedelta(days=14 * i)).isoformat(), "duration": 14}
               for i in range(sprints)]
        graphql(create, p=pid, n=F_ITER, t="ITERATION", o=None,
                c={"startDate": start, "duration": 14, "iterations": its})
    status = have.get(F_STATUS)
    if status and set(status.get("options", {})) != {s for s, _ in STATUSES}:
        graphql("""mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]){ updateProjectV2Field(
                   input:{fieldId:$f,singleSelectOptions:$o}){ clientMutationId } }""",
                f=status["id"], o=[{"name": s, "color": c, "description": ""} for s, c in STATUSES])
    return refresh_fields(state)


def make_public(state):
    graphql("""mutation($p:ID!,$d:String!){ updateProjectV2(input:{projectId:$p,public:true,shortDescription:$d}){
               clientMutationId } }""",
            p=state["project_id"], d="LAB-5: backlog break từ spec LAB-4 (epic → issue → sub-issue), SWP + giờ, sprint giả lập")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprints", type=int, default=10)
    ap.add_argument("--start", default="2027-02-01")
    a = ap.parse_args()
    state = ensure_fields(ensure_project(load_json(STATE_FILE, {})), a.sprints, a.start)
    make_public(state)
    print(state["url"], sorted(state["fields"]))


if __name__ == "__main__":
    main()
