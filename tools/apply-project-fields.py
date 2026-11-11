"""Apply Project field values from a JSON file keyed by backlog key. Idempotent (re-setting a value is harmless).

Input JSON: {"E07-03": {"Iteration": "Sprint 1", "Status": "Done", "Phụ trách (giả định)": "BE-1", "SWP": 6}, ...}
Field names must match tools/project-state.json; a value of null clears the field.
Usage: python tools/apply-project-fields.py sprint-plan/sprint-assignments.json [--close-done]
"""
import json
import sys

from github_api_client import rest
from project_state import MAP_FILE, OWNER, REPO, STATE_FILE, load_json, refresh_fields, set_field, set_fields_batch


def main():
    values = json.loads(open(sys.argv[1], encoding="utf-8").read())
    state = refresh_fields(load_json(STATE_FILE, {}))
    imap = load_json(MAP_FILE, {})
    missing = [k for k in values if k not in imap]
    if missing:
        sys.exit(f"keys not on GitHub yet: {missing[:10]}")
    triples = [(imap[k]["item_id"], name, v) for k, fields in values.items() for name, v in fields.items()
               if v is not None]
    set_fields_batch(state, triples)
    for k, fields in values.items():  # clearing a field has no batch form; rare
        for name, v in fields.items():
            if v is None:
                set_field(state, imap[k]["item_id"], name, None)
    print(f"applied {len(triples)} field values on {len(values)} items")
    if "--close-done" in sys.argv:  # issue state follows board Status: Done → closed (completed)
        done = [k for k, f in values.items() if f.get("Status") == "Done"]
        for k in done:
            rest("PATCH", f"/repos/{OWNER}/{REPO}/issues/{imap[k]['number']}",
                 {"state": "closed", "state_reason": "completed"})
        print(f"closed {len(done)} issues")


if __name__ == "__main__":
    main()
