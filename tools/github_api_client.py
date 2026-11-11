"""Thin wrapper around the `gh` CLI for REST + GraphQL calls (auth comes from `gh auth`).

Retries GitHub secondary rate limits with backoff so long bulk runs can be resumed safely.
"""
import json
import subprocess
import sys
import time

GH = "gh"


def _run(args, payload=None, retries=6):
    """Run `gh api ...`; payload (dict) is sent as JSON on stdin. Returns parsed JSON or None."""
    for attempt in range(retries):
        proc = subprocess.run(
            [GH, "api", *args],
            input=json.dumps(payload) if payload is not None else None,
            capture_output=True, text=True, encoding="utf-8",
        )
        if proc.returncode == 0:
            out = proc.stdout.strip()
            return json.loads(out) if out else None
        err = proc.stderr + proc.stdout
        if "rate limit" in err.lower() or "abuse" in err.lower() or "HTTP 403" in err and "secondary" in err:
            wait = 60 * (attempt + 1)
            print(f"  rate limited, sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        if any(code in err for code in ("HTTP 502", "HTTP 503", "HTTP 504")):
            print(f"  server error, retry {attempt + 1}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
            continue
        raise RuntimeError(f"gh api {' '.join(args)} failed: {err.strip()[:800]}")
    raise RuntimeError(f"gh api {' '.join(args)}: rate limit retries exhausted")


def rest(method, path, body=None):
    args = ["-X", method, path, "-H", "Accept: application/vnd.github+json"]
    if body is not None:
        args += ["--input", "-"]
    return _run(args, body)


def graphql(query, **variables):
    data = _run(["graphql", "--input", "-"], {"query": query, "variables": variables})
    if data and data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], ensure_ascii=False)[:800])
    return data["data"]
