# Labs Activity Reports

This repository tracks GitHub activity for LF Decentralized Trust labs and flags labs that appear to be inactive. The set of tracked labs and their repositories is defined in [repos.json](repos.json), and the reports are generated from the GitHub API by [generate_activity.sh](generate_activity.sh).

Repositories listed in [excluded-repos.json](excluded-repos.json) are skipped: they are neither queried nor reported, and a lab whose every repository is excluded does not appear in any report. Use it to drop a repository from the reports without removing it from [repos.json](repos.json).

Separately, [reconcile.py](reconcile.py) checks weekly whether [repos.json](repos.json) still matches reality and writes [unlisted-labs.md](unlisted-labs.md). It never edits [repos.json](repos.json) itself: naming a lab, deciding whether one has graduated to a project, and grouping repositories under a lab entry are judgement calls, so the report describes the drift and a person makes the edit.

## Reports

| File | Contents | Criteria |
| :--- | :--- | :--- |
| [activity.md](activity.md) | The full activity report: for every tracked repository, the timestamp of its latest commit push, latest pull request update, and latest issue update, grouped by lab. | All tracked labs, regardless of activity level. |
| [evaluate.md](evaluate.md) | Labs that should be evaluated for continued viability. | No activity in any of the lab's repositories in the last **three months**, but activity within the last six months. |
| [at-risk.md](at-risk.md) | Labs considered at risk of being archived or retired. | No activity in any of the lab's repositories in the last **six months**. |
| [unlisted-labs.md](unlisted-labs.md) | Where the tracked set has drifted from the LFDT Labs site, the lab-proposals tracker and the enterprise repository inventory. | Regenerated weekly; not about activity. |

## How labs are classified

A lab's "most recent activity" is the latest of the last commit push, pull request update, or issue update across **all** of the lab's tracked repositories, as reported in [activity.md](activity.md). A lab with several dormant repositories is still considered active if at least one repository has recent activity.

- **Active** — most recent activity within the last three months. Appears only in [activity.md](activity.md).
- **Evaluate** — most recent activity more than three months ago but within the last six months. Listed in [evaluate.md](evaluate.md).
- **At risk** — most recent activity more than six months ago (or no recorded activity at all). Listed in [at-risk.md](at-risk.md). At-risk labs are not repeated in [evaluate.md](evaluate.md), even though they also meet the three-month criterion.

The evaluate and at-risk reports include a summary table of flagged labs followed by a per-lab breakdown showing the last recorded activity for each repository.
