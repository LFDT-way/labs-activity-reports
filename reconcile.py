#!/usr/bin/env python3
"""Reconcile repos.json against the three sources that describe LFDT labs.

Writes unlisted-labs.md. Deliberately never edits repos.json: deciding what a
lab is called, whether one has graduated to a project, whether an archived page
is stale, and which repositories belong under which lab entry all need a human.
This reports the drift and leaves the edit to a person.

Sources, in order of authority for "what is a lab":

  labs/approved on the LFDT Labs site  the canonical lab list and lab titles
  LF-Decentralized-Trust/lab-proposals which labs are approved, and which are
                                       still mid-onboarding
  LFDT-way/gh-data                     the enterprise inventory of public,
                                       non-archived repositories

The inventory alone is not enough: it knows organizations and repositories, not
labs. Labs hosted inside the hyperledger, hyperledger-labs and
LF-Decentralized-Trust-labs umbrella organizations have no per-lab organization
to key on, and LFDT-tegaris has no organization description at all.

GITHUB_TOKEN is optional but strongly preferred; without it the GitHub API
allows 60 requests an hour and this makes rather more than that.
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request

INVENTORY_URL = (
    "https://raw.githubusercontent.com/LFDT-way/gh-data/main/lf-decentralized-trust.json"
)
LABS_SITE = "LF-Decentralized-Trust-labs/LF-Decentralized-Trust-labs.github.io"
PROPOSALS = "LF-Decentralized-Trust/lab-proposals"
API = "https://api.github.com"

LAB_TRAILER = "an LF Decentralized Trust lab."
PROJECT_TRAILER = "an LF Decentralized Trust project."

TOKEN = os.environ.get("GITHUB_TOKEN", "")


def fetch(url, accept="application/vnd.github+json", anon=False):
    """GET a URL, returning (status, body). Falls back to an unauthenticated
    request on 403: some organizations (LFDT-Lineth) refuse classic tokens but
    answer fine with no credentials at all."""
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "lfdt-reconcile"})
    if TOKEN and not anon:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        if e.code == 403 and TOKEN and not anon:
            return fetch(url, accept, anon=True)
        return e.code, e.read()
    except urllib.error.URLError as e:
        print(f"  warning: {url}: {e}", file=sys.stderr)
        return 0, b""


def fetch_json(url, **kw):
    status, body = fetch(url, **kw)
    if status != 200:
        return status, None
    try:
        return status, json.loads(body)
    except json.JSONDecodeError:
        return status, None


def paged(url):
    """Walk a paginated API listing."""
    out, page = [], 1
    sep = "&" if "?" in url else "?"
    while True:
        status, data = fetch_json(f"{url}{sep}per_page=100&page={page}")
        if status != 200 or not isinstance(data, list):
            break
        out.extend(data)
        if len(data) < 100:
            break
        page += 1
    return out


def load_tracked():
    labs = json.load(open("repos.json"))["labs"]
    tracked = {}
    for lab in labs:
        for r in lab["repositories"]:
            tracked[(r["org"].lower(), r["name"].lower())] = (
                lab["display_name"],
                f"{r['org']}/{r['name']}",
            )
    excluded = set()
    if os.path.exists("excluded-repos.json"):
        for e in json.load(open("excluded-repos.json")).get("excluded", []):
            excluded.add((e["org"].lower(), e["name"].lower()))
    return labs, tracked, excluded


def load_inventory():
    status, data = fetch_json(INVENTORY_URL, accept="application/json")
    if status != 200 or not data:
        sys.exit(f"error: could not read the inventory ({status}): {INVENTORY_URL}")
    repos = {(r["org"].lower(), r["name"].lower()): r for r in data["repositories"]}
    return data["organizations"], repos


def load_labs_site():
    """Returns ({title: {'slug','orgs','repos'}}, {archived slugs})."""
    status, tree = fetch_json(f"{API}/repos/{LABS_SITE}/git/trees/HEAD?recursive=1")
    if status != 200 or not tree:
        sys.exit(f"error: could not read the labs site tree ({status})")

    approved, archived = {}, set()
    for entry in tree.get("tree", []):
        path = entry.get("path", "")
        if path.startswith("labs/archived/") and path.endswith(".md"):
            archived.add(os.path.basename(path)[:-3].lower())
        elif path.startswith("labs/approved/") and path.endswith(".md"):
            approved[path] = entry["sha"]

    labs = {}
    for path, sha in sorted(approved.items()):
        status, body = fetch(f"{API}/repos/{LABS_SITE}/git/blobs/{sha}")
        if status != 200:
            continue
        try:
            text = base64.b64decode(json.loads(body)["content"]).decode("utf-8", "replace")
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
        m = re.search(r"^title:\s*(.+)$", text, re.M)
        title = m.group(1).strip() if m else os.path.basename(path)[:-3]

        def links_in(s):
            found = re.findall(r"github\.com/([A-Za-z0-9_.-]+)(?:/([A-Za-z0-9_.-]+))?", s)
            return (
                {a.lower() for a, _ in found},
                {(a.lower(), b.lower()) for a, b in found if b},
            )

        # Links anywhere on the page, used to decide whether a lab is
        # represented at all. Generous on purpose: a page may point at its
        # repositories from any section.
        all_orgs, all_repos = links_in(text)

        # Links in the page's own "Lab Name" section, which is where a page
        # declares what it *is*. The rest of a page also cites committer
        # profiles, upstream projects and related repositories, so the wider
        # set cannot be read as "this lab owns that repository".
        # Match any heading level: 60 pages write "# Lab Name" and 7 write
        # "### Lab Name", and the stop-lookahead has to accept any level too,
        # or a page whose next heading is deeper runs on to end of file and
        # drags in every link it cites.
        section = re.search(r"#+\s*Lab Name\s*\n+(.*?)(?=\n#+\s|\Z)", text, re.S)
        own_orgs, own_repos = links_in(section.group(1)) if section else (set(), set())

        labs[title] = {
            "slug": os.path.basename(path)[:-3],
            "orgs": all_orgs,
            "repos": all_repos,
            "own_orgs": own_orgs,
            "own_repos": own_repos,
        }
    return labs, archived


def load_proposals():
    issues = paged(f"{API}/repos/{PROPOSALS}/issues?state=all")
    approved, onboarding, proposed = [], [], []
    for i in issues:
        if "pull_request" in i:
            continue
        title, labels = i["title"], {l["name"] for l in i.get("labels", [])}
        if i["state"] == "closed" and "Approved" in labels:
            approved.append(i)
        elif i["state"] == "open" and title.startswith("[Lab Onboarding]"):
            onboarding.append(i)
        elif i["state"] == "open" and title.startswith("[Lab Proposal]"):
            proposed.append(i)
    key = lambda i: i["number"]
    return sorted(approved, key=key), sorted(onboarding, key=key), sorted(proposed, key=key)


def load_org_descriptions(orgs):
    out = {}
    for org in orgs:
        status, data = fetch_json(f"{API}/orgs/{org}")
        out[org] = (data or {}).get("description") or "" if status == 200 else None
    return out


def repo_state(full_name):
    """Why a tracked repository is missing from the inventory."""
    status, data = fetch_json(f"{API}/repos/{full_name}")
    if status == 404:
        return "deleted or renamed beyond redirect"
    if status != 200 or not data:
        return f"unverifiable (HTTP {status})"
    if data["full_name"].lower() != full_name.lower():
        return f"moved to `{data['full_name']}`"
    if data.get("archived"):
        return "archived"
    if data.get("private"):
        return "private"
    if data.get("visibility", "").upper() == "INTERNAL":
        return "internal"
    return "public and unarchived, but absent from the inventory"


def md_table(header, rows):
    if not rows:
        return "_None._\n"
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join([":---"] * len(header)) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def main():
    labs_json, tracked, excluded = load_tracked()
    tracked_orgs = {o for o, _ in tracked}
    display_names = {l["display_name"] for l in labs_json}

    print("reading the inventory, the labs site and the proposal tracker...")
    inv_orgs, inv_repos = load_inventory()
    site_labs, site_archived = load_labs_site()
    approved_issues, onboarding, proposed = load_proposals()
    descriptions = load_org_descriptions(inv_orgs)
    print(
        f"  inventory: {len(inv_orgs)} organizations, {len(inv_repos)} repositories\n"
        f"  labs site: {len(site_labs)} approved, {len(site_archived)} archived\n"
        f"  proposals: {len(approved_issues)} approved, {len(onboarding)} onboarding, "
        f"{len(proposed)} under review"
    )

    # 1. Approved labs with nothing of theirs in repos.json.
    inv_org_set = {o.lower() for o in inv_orgs}
    uncovered = []
    for title, info in sorted(site_labs.items()):
        if title in display_names or info["repos"] & set(tracked) or info["orgs"] & tracked_orgs:
            continue
        # A page's links are mostly maintainer profiles, so only count ones
        # that name an enterprise organization or a repository inside one.
        where = sorted(f"`{a}/{b}`" for a, b in info["repos"] if a in inv_org_set)
        where = where or sorted(f"`{o}`" for o in info["orgs"] if o in inv_org_set)
        uncovered.append(
            (title, info["slug"], ", ".join(where) or "_names no organization or repository_")
        )

    # 2. Organizations whose description carries the lab trailer but which
    #    repos.json never references.
    lab_orgs = [o for o in inv_orgs if (descriptions.get(o) or "").strip().endswith(LAB_TRAILER)]
    missing_orgs = []
    for org in lab_orgs:
        if org.lower() in tracked_orgs:
            continue
        work = sorted(
            n for (o, n) in inv_repos if o == org.lower() and n not in {".github", "governance", "tsc", "wiki"}
        )
        missing_orgs.append((org, ", ".join(f"`{w}`" for w in work) or "_none_"))

    # 3. Tracked repositories the inventory no longer lists.
    vanished = []
    for key, (lab, full) in sorted(tracked.items(), key=lambda kv: kv[1][1]):
        if key in inv_repos:
            continue
        note = "excluded from reports" if key in excluded else ""
        vanished.append((f"`{full}`", lab, repo_state(full), note))

    # What approved lab pages claim as their own, from their "Lab Name"
    # sections rather than from every link on the page.
    approved_repos, approved_orgs = set(), set()
    for info in site_labs.values():
        approved_repos |= info["own_repos"]
        approved_orgs |= info["own_orgs"]

    def page_for(org, name):
        for title, info in site_labs.items():
            if (org, name) in info["own_repos"]:
                return "approved", f"`labs/approved/{info['slug']}.md`"
        if name in site_archived:
            return "archived", f"`labs/archived/{name}.md`"
        return "none", "_none_"

    # 4. Repositories in tracked organizations that repos.json does not list.
    #
    #    repos.json references the hyperledger and LF-Decentralized-Trust
    #    organizations only because a few labs were onboarded inside them, so
    #    listing everything they hold would bury the real candidates under the
    #    Fabric project and the foundation's own repositories. Treat a
    #    repository as a candidate only when its organization is a single-lab
    #    one, or an umbrella labs organization, or an approved lab page names
    #    the repository outright.
    ADMIN = {".github", "governance", "tsc", "wiki"}
    new_repos = []
    for (org, name), r in sorted(inv_repos.items()):
        if org not in tracked_orgs or (org, name) in tracked or name in ADMIN:
            continue
        desc = (descriptions.get(r["org"]) or "").strip()
        is_lab_org = desc.endswith(LAB_TRAILER)
        is_umbrella = org.endswith("-labs")
        if not (is_lab_org or is_umbrella or (org, name) in approved_repos):
            continue
        kind, page = page_for(org, name)
        new_repos.append((f"`{r['org']}/{r['name']}`", page, r.get("description") or ""))

    # 5. Tracked repositories whose only lab page is an archived one. A name
    #    collision is not enough: hyperledger-labs/signare is the archived lab,
    #    while LFDT-Smoot/signare is a live repository of an approved one, and
    #    solang has both an approved and an archived page.
    archived_pages = []
    for key, (lab, full) in sorted(tracked.items(), key=lambda kv: kv[1][1]):
        org, name = key
        if name not in site_archived:
            continue
        if key in approved_repos or org in approved_orgs or lab in site_labs:
            continue
        archived_pages.append((f"`{full}`", lab, f"`labs/archived/{name}.md`"))

    lines = []
    w = lines.append
    w("# Labs reconciliation\n")
    w(
        "Generated by [reconcile.py](reconcile.py) from the "
        f"[LFDT Labs site](https://github.com/{LABS_SITE}/tree/main/labs), the "
        f"[lab-proposals tracker](https://github.com/{PROPOSALS}/issues) and the "
        "[enterprise inventory](https://github.com/LFDT-way/gh-data) "
        "published from `github-audit-tools`.\n"
    )
    plural = lambda n, one, many: one if n == 1 else many

    w("## BLUF\n")
    w(
        f"[repos.json](repos.json) tracks **{len(labs_json)} labs across {len(tracked)} "
        f"repositories**. The labs site lists **{len(site_labs)} approved labs**, of which "
        f"**{len(site_labs) - len(uncovered)}** have at least one repository tracked here and "
        f"**{len(uncovered)}** {plural(len(uncovered), 'does', 'do')} not. Of the "
        f"{len(lab_orgs)} organizations whose description carries the lab trailer, "
        f"**{len(missing_orgs)}** {plural(len(missing_orgs), 'is', 'are')} not referenced. "
        f"**{len(vanished)}** tracked {plural(len(vanished), 'repository is', 'repositories are')} "
        f"no longer in the inventory, and **{len(new_repos)}** inventory "
        f"{plural(len(new_repos), 'repository', 'repositories')} in tracked organizations "
        f"{plural(len(new_repos), 'is', 'are')} not listed.\n"
    )
    w(
        "This file is generated. `repos.json` is **not** edited automatically: naming a lab, "
        "deciding whether one has graduated to a project, and grouping repositories under a lab "
        "entry are judgement calls. Use the tables below to make those edits by hand.\n"
    )

    w("## Approved labs with no tracked repository\n")
    w(md_table(["Lab", "Labs site page", "Repositories or organization named"],
               [(t, f"`labs/approved/{s}.md`", w_) for t, s, w_ in uncovered]))

    w("\n## Lab-trailer organizations not referenced in repos.json\n")
    w(md_table(["Organization", "Non-administrative repositories"],
               [(f"[{o}](https://github.com/{o})", r) for o, r in missing_orgs]))
    w(
        "\nThe trailer is not a sufficient discovery rule on its own: it misses any lab hosted "
        "inside an umbrella organization, and any organization with no description set. The "
        "approved-labs table above is the reliable check.\n"
    )

    w("\n## Tracked repositories missing from the inventory\n")
    w(
        "The inventory lists public, non-archived repositories only, so anything here has been "
        "archived, made private, renamed, moved or deleted.\n\n"
    )
    w(md_table(["Repository", "Lab entry", "Current state", "Note"], vanished))

    w("\n## Candidate additions\n")
    w(
        "Repositories in a single-lab or umbrella labs organization, or named by an approved lab "
        "page, that repos.json does not list. A page of `_none_` means no lab page mentions the "
        "repository, and an `labs/archived/` page means the lab was retired and the repository "
        "should probably be left alone. Administrative repositories (`.github`, `governance`, "
        "`tsc`, `wiki`) are omitted.\n\n"
    )
    w(md_table(["Repository", "Labs site page", "Description"], new_repos))

    w("\n## Tracked repositories whose lab page is archived\n")
    w(md_table(["Repository", "Lab entry", "Labs site page"], archived_pages))

    w("\n## Migration in progress\n")
    w(
        "Open `[Lab Onboarding]` issues. A lab here may have no repository yet, or a seed "
        "repository that will read as inactive until its code lands.\n\n"
    )
    # The onboarding issue titles are free text, so match them to a labs site
    # page on alphanumerics alone: "Proof of Control" has to reach
    # "Open Verification Proof-of-Control".
    squash = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    uncovered_titles = {t for t, _, _ in uncovered}

    def onboarding_row(issue):
        name = issue["title"].replace("[Lab Onboarding]", "").strip()
        key = squash(name)
        for title in site_labs:
            if squash(title) == key or key in squash(title) or squash(title) in key:
                state = "no" if title in uncovered_titles else "yes"
                return name, f"`labs/approved/{site_labs[title]['slug']}.md`", state
        return name, "_no matching page_", "unknown"

    w(md_table(
        ["Issue", "Lab", "Labs site page", "Tracked"],
        [
            (f"[#{i['number']}](https://github.com/{PROPOSALS}/issues/{i['number']})", *onboarding_row(i))
            for i in onboarding
        ],
    ))

    w("\n## Proposals under review\n")
    w(
        "Not yet approved, so normally no repository to track.\n\n"
    )
    w(md_table(
        ["Issue", "Proposal", "Labels"],
        [
            (
                f"[#{i['number']}](https://github.com/{PROPOSALS}/issues/{i['number']})",
                i["title"].replace("[Lab Proposal]", "").strip(),
                ", ".join(sorted(l["name"] for l in i.get("labels", []))) or "_none_",
            )
            for i in proposed
        ],
    ))

    with open("unlisted-labs.md", "w") as fh:
        fh.write("\n".join(lines))

    # The BLUF doubles as the Actions job summary, so the drift is visible
    # without opening the file.
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write("\n".join(lines[:6]) + "\n")

    print(
        f"unlisted-labs.md: {len(uncovered)} uncovered approved labs, "
        f"{len(missing_orgs)} unreferenced lab orgs, {len(vanished)} vanished repos, "
        f"{len(new_repos)} candidate additions, {len(archived_pages)} archived-page repos"
    )


if __name__ == "__main__":
    main()
