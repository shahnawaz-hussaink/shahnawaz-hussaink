"""Refresh the live blocks in README.md.

Rewrites the text between these marker pairs and leaves everything else alone:
  <!-- stats:start -->    / <!-- stats:end -->     GitHub + LeetCode numbers
  <!-- activity:start --> / <!-- activity:end -->  recent public GitHub events

Standard library only. If one source fails, that block keeps its old content.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

GITHUB_USER = "shahnawaz-hussaink"
LEETCODE_USER = "shahnawazhussaink"
README = os.path.join(os.path.dirname(__file__), "..", "README.md")
ACTIVITY_LINES = 6


def fetch(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": GITHUB_USER, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.load(res)


def github(path):
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    return fetch(f"https://api.github.com{path}", headers=headers)


def github_stats():
    user = github(f"/users/{GITHUB_USER}")
    repos = github(f"/users/{GITHUB_USER}/repos?per_page=100&type=owner")
    stars = sum(r["stargazers_count"] for r in repos if not r["fork"])
    return {"public_repos": user["public_repos"], "stars_earned": stars, "followers": user["followers"]}


def leetcode_stats():
    query = '{ matchedUser(username: "%s") { submitStats { acSubmissionNum { difficulty count } } } }' % LEETCODE_USER
    body = json.dumps({"query": query}).encode()
    res = fetch("https://leetcode.com/graphql", body, {"Content-Type": "application/json", "Referer": "https://leetcode.com"})
    counts = {row["difficulty"]: row["count"] for row in res["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]}
    return {"solved": counts["All"], "easy": counts["Easy"], "medium": counts["Medium"], "hard": counts["Hard"]}


def describe(event):
    repo = event["repo"]["name"]
    short = repo.split("/", 1)[1] if repo.startswith(f"{GITHUB_USER}/") else repo
    p, kind = event["payload"], event["type"]
    if kind == "PushEvent":
        return "PUSH ", f"{short} → {p.get('ref', '').removeprefix('refs/heads/')}"
    if kind == "PullRequestEvent" and p.get("action") in ("opened", "merged", "closed"):
        merged = p["action"] == "merged" or p.get("pull_request", {}).get("merged")
        label = "MERGE" if merged else {"opened": "PR   ", "closed": "CLOSE"}[p["action"]]
        return label, f"{short}#{p['number']}"
    if kind == "CreateEvent":
        return "NEW  ", short if p.get("ref_type") == "repository" else f"{p.get('ref_type')} {p.get('ref')} in {short}"
    if kind == "ReleaseEvent":
        return "SHIP ", f"{short} {p.get('release', {}).get('tag_name', '')}".strip()
    if kind == "IssuesEvent" and p.get("action") == "opened":
        return "ISSUE", f"{short}#{p['issue']['number']}"
    if kind == "WatchEvent":
        return "STAR ", short
    if kind == "ForkEvent":
        return "FORK ", short
    return None


def activity():
    lines, seen = [], set()
    events = github(f"/users/{GITHUB_USER}/events/public?per_page=100")
    for event in sorted(events, key=lambda e: e["created_at"], reverse=True):
        if event["repo"]["name"] == f"{GITHUB_USER}/{GITHUB_USER}":
            continue  # skip this profile repo, including the bot's own commits
        described = describe(event)
        if not described or described in seen:
            continue
        seen.add(described)
        when = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
        lines.append(f"[{when}] {described[0]}  {described[1]}")
        if len(lines) == ACTIVITY_LINES:
            break
    return lines


def replace_block(text, name, body):
    pattern = re.compile(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"marker '{name}' not found in README.md")
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), text)


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()

    stats = {}
    for key, source in (("github", github_stats), ("leetcode", leetcode_stats)):
        try:
            stats[key] = source()
        except Exception as err:  # keep going; the other source may still work
            print(f"{key}: {err}", file=sys.stderr)

    if len(stats) == 2:
        stats["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rows = ",\n".join(f'  "{k}": {json.dumps(v, separators=(", ", ": "))}' for k, v in stats.items())
        text = replace_block(text, "stats", "```json\n{\n" + rows + "\n}\n```")

    try:
        lines = activity()
        if lines:
            text = replace_block(text, "activity", "```console\n" + "\n".join(lines) + "\n```")
    except Exception as err:
        print(f"activity: {err}", file=sys.stderr)

    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
