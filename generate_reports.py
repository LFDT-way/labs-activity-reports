#!/usr/bin/env python3
"""Generate evaluate.md and at-risk.md from activity.md.

A lab's most recent activity is the latest of the last commit push, pull
request update, or issue update across all of its tracked repositories.
Labs inactive for more than three months go to evaluate.md; labs inactive
for more than six months go to at-risk.md instead.
"""

import datetime
import re
import sys

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


def months_ago(date, months):
    month = date.month - months
    year = date.year
    while month < 1:
        month += 12
        year -= 1
    day = min(date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                         31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return datetime.date(year, month, day)


def parse_activity(path):
    labs = {}
    generated = None
    cur = None
    with open(path) as f:
        for line in f:
            m = re.match(r"^\*\*Last updated: (.+ UTC)\*\*", line)
            if m:
                generated = m.group(1)
                continue
            m = re.match(r"^## (.+)$", line)
            if m:
                cur = m.group(1).strip()
                labs[cur] = []
                continue
            if cur and line.startswith("|") and "Repository" not in line and ":---" not in line:
                repo = line.split("|")[1].strip()
                dates = DATE_RE.findall(line)
                labs[cur].append((repo, max(dates) if dates else None))
    return generated, labs


def section(entries):
    out = ["| Lab | Most Recent Activity | Repositories |", "| :--- | :--- | :--- |"]
    for lab, latest, repos in entries:
        out.append(f"| {lab} | {latest or 'n/a'} | {len(repos)} |")
    out.append("")
    for lab, latest, repos in entries:
        out.append(f"## {lab}")
        out.append("")
        out.append("| Repository | Last Activity | Link |")
        out.append("| :--- | :--- | :--- |")
        for repo, d in sorted(repos, key=lambda r: r[1] or "0000", reverse=True):
            out.append(f"| {repo} | {d or 'n/a'} | [github.com/{repo}](https://github.com/{repo}) |")
        out.append("")
    return "\n".join(out)


def main():
    generated, labs = parse_activity("activity.md")
    today = datetime.date.today()
    three = months_ago(today, 3)
    six = months_ago(today, 6)

    evaluate, at_risk = [], []
    for lab, repos in labs.items():
        dates = [d for _, d in repos if d]
        latest = max(dates) if dates else None
        latest_day = datetime.date.fromisoformat(latest[:10]) if latest else None
        if latest_day is None or latest_day < six:
            at_risk.append((lab, latest, repos))
        elif latest_day < three:
            evaluate.append((lab, latest, repos))

    evaluate.sort(key=lambda e: e[1] or "0000")
    at_risk.sort(key=lambda e: e[1] or "0000")

    common = (
        "A lab's \"most recent activity\" is the latest of the last commit push, pull request "
        "update, or issue update across all of its tracked repositories, as reported in "
        "[activity.md](activity.md)."
    )
    source = f"based on [activity.md](activity.md) generated {generated}" if generated else "based on [activity.md](activity.md)"

    with open("evaluate.md", "w") as f:
        f.write(f"""# Labs to Evaluate

**Report date: {today} ({source})**

Labs listed here have had **no activity in the last three months** (no activity since {three}), but have had activity within the last six months. These labs should be evaluated for continued viability. Labs with no activity for more than six months are escalated to [at-risk.md](at-risk.md) and are not repeated here.

{common}

""")
        f.write(section(evaluate))

    with open("at-risk.md", "w") as f:
        f.write(f"""# At-Risk Labs

**Report date: {today} ({source})**

Labs listed here have had **no activity in the last six months** (no activity since {six}). These labs are considered at risk of being archived or retired.

{common}

""")
        f.write(section(at_risk))

    print(f"evaluate.md: {len(evaluate)} labs; at-risk.md: {len(at_risk)} labs")


if __name__ == "__main__":
    sys.exit(main())
