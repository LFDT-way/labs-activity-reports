# Labs reconciliation

Generated 2026-10-28. Reconciles [repos.json](repos.json) against three sources:

| Source | Used for |
| :--- | :--- |
| `lf-decentralized-trust.yaml` | the 58 enterprise orgs and their 570 public, non-archived repositories |
| [LF-Decentralized-Trust/lab-proposals](https://github.com/LF-Decentralized-Trust/lab-proposals/issues) | which labs are approved (closed issues, `Approved` label) and which are mid-migration (open `[Lab Onboarding]` issues) |
| [LFDT Labs site](https://github.com/LF-Decentralized-Trust-labs/LF-Decentralized-Trust-labs.github.io) `labs/approved` + `labs/archived` | the canonical lab list, lab titles, and each lab's repositories |

## BLUF

repos.json now tracks **55 labs across 134 repositories**, up from 47 labs / 114 repositories.
**68 of the 69 approved labs** on the LFDT Labs site have at least one repository tracked. The one
exception, **DAS Interoperability Lab**, is approved but has no GitHub org or repository yet, so
there is nothing to track. Of the 22 orgs carrying the labs description trailer, 21 are
referenced; the 22nd, `OpenReagent`, holds only a `governance` repository because its lab renamed
to `Sigvelis`.

## Approved labs added this pass

Three approved labs were missing because their repositories do not live in a labs-tagged org —
`fabric-chaincode-python` and `fabric-x-migrate` were onboarded into the `hyperledger` org, and
`LFDT-tegaris` has no org description at all.

| Lab | Repository | Proposal | Onboarding | Newest push |
| :--- | :--- | :--- | :--- | :--- |
| Fabric Chaincode Python | `hyperledger/fabric-chaincode-python` | [#6](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/6) approved | [#17](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/17) complete | 2026-10-23 |
| Fabric-X-Migrate | `hyperledger/fabric-x-migrate` | [#21](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/21) approved | [#25](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/25) open | 2026-10-21 |
| Tegaris Application Privacy | `LFDT-tegaris/tegaris` | [#11](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/11) approved | [#19](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/19) open | 2026-10-21 |

`LFDT-tegaris/tegaris` was created 2026-10-21 and is a 5 KB seed repository — the proposal states
the source contribution follows release preparation, and onboarding #19 still has "move your lab
to an LFDT hosted GitHub organization" unchecked. Expect it to read as inactive until the code
lands.

`SmartBFT` was also restored, at its new path `hyperledger/SmartBFT` (was
`hyperledger-labs/SmartBFT`). The move into the `hyperledger` org initially looked like a
graduation to project status, but that org demonstrably hosts labs, the repository is live and
unarchived, and `labs/approved/smartbft.md` still lists it.

## Labs orgs added earlier this pass

All six were approved labs with no entry at all; display names are the `title` from each lab's
`labs/approved` page.

| Lab entry | Org | Work repositories | Proposal |
| :--- | :--- | :--- | :--- |
| Blockchain Decentralisation Index | `Blockchain-Decentralisation-Index` | `consensus-`, `network-`, `software-`, `tokenomics-decentralization` | [#4](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/4) |
| CLPR | `LFDT-CLPR` | `clpr-endpoint`, `clpr-smart-contracts`, `clpr-spec` | [#5](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/5) |
| Composable Evidence Criteria | `Composable-Evidence-Criteria` | `action-ref-conformance` | [#2](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/2) (as `recomputable-evidence`) |
| Permissioned Privacy Control | `LFDT-Permissioned-Privacy-Control` | `permissioned-privacy-control` | [#3](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/3) (as `Open Privacy Suite`) |
| Sigvelis | `Sigvelis` | `sigvelis` | — (renamed from OpenReagent) |
| Smoot | `LFDT-Smoot` | `bridge`, `signare` | — |

`LFDT-Smoot/signare` is correctly tracked. The archived `Signare` lab is a different repository,
[`hyperledger-labs/signare`](https://github.com/hyperledger-labs/signare), archived with its last
push in December 2024; `LFDT-Smoot/signare` is a live 42 MB repository pushed 2026-10-27.

Per-org administrative repositories (`.github`, `governance`, `tsc`/`TSC`, `wiki`) are excluded
from new entries: they receive bot and LFDT-staff pushes that would mask dormancy in
[evaluate.md](evaluate.md) and [at-risk.md](at-risk.md). Five such entries predate this pass and
were left in place.

## Migration in progress

Open `[Lab Onboarding]` issues. The "org moved" column is the *Work with LFDT staff to move your
lab to an LFDT hosted GitHub organization* checkbox.

| Issue | Lab | Org moved | Tracked in repos.json |
| :--- | :--- | :--- | :--- |
| [#8](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/8) | CLPR | yes — `LFDT-CLPR` | yes |
| [#12](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/12) | Proof of Control | yes — `LFDT-ProofOfControl` | yes |
| [#15](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/15) | Blockchain Decentralisation Index | yes — `Blockchain-Decentralisation-Index` | yes |
| [#19](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/19) | Tegaris Application Privacy | **no** | yes — seed repo only |
| [#20](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/20) | Recomputable Evidence | **no** | yes — as `Composable Evidence Criteria` |
| [#24](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/24) | Permissioned Privacy Control | yes — `LFDT-Permissioned-Privacy-Control` | yes |
| [#25](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/25) | Fabric-X-Migrate | repo already in `hyperledger` | yes |

Issue #20 is still titled `recomputable-evidence` and its "pick a name" box is unchecked, but the
org `Composable-Evidence-Criteria` and the `labs/approved/composable-evidence-criteria.md` page
both exist — proposal #2 listed `composable-evidence-criteria` as the fallback name. Watch for a
rename in either direction.

Two proposals are still under review and have no repositories, so nothing to track yet:
[#26 VC Profile Validator](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/26) and
[#29 OpenCrMS](https://github.com/LF-Decentralized-Trust/lab-proposals/issues/29), both labelled
`New Proposal` / `Steward Review`.

## Approved labs still untracked

| Lab | Why |
| :--- | :--- |
| DAS Interoperability Lab | Approved page exists but names no GitHub org or repository — only maintainer profiles. No proposal issue in `lab-proposals` either; it predates that repo or was handled elsewhere. Nothing to track. |

## Repositories dropped from repos.json

| Repository | Reason | Approved page still present? |
| :--- | :--- | :--- |
| `hyperledger-labs/harmonia` | archived on GitHub (excluded from the yaml) | yes — `labs/approved/harmonia.md` is stale |
| `hyperledger-labs/fabric-token-sdk` | moved to `LFDT-Panurus/panurus`; that org's description reads *"Panurus, an LF Decentralized Trust **project**"*, so it graduated out of labs | yes — `labs/approved/fabric-token-sdk.md` is stale |
| `hyperledger-cello/cello-analytics` | archived on GitHub | n/a (part of the Cello lab) |
| `hyperledger-solang/solang-vscode` | archived on GitHub | n/a (part of the Solang lab) |
| `OpenReagent/openreagent` | moved to `Sigvelis/sigvelis` | replaced by `labs/approved/sigvelis.md` |

Three stale org names were also corrected: `aeoess` and `LFDT-Agent-Passport-System` →
`Agent-Authority-Conformance`, and `LFDT-OpenVerification` → `LFDT-ProofOfControl`.

## Open questions

1. **`Agent Passport System` display name is stale.** The lab is titled *Agent Authority
   Conformance* on the site and in proposal issue titles. Renaming the repos.json entry would
   change a heading in [activity.md](activity.md).
2. **Grouped lab entries hide dormancy.** `Fabric labs` holds 10 repositories that the site lists
   as 10 separate approved labs, `Aries labs` holds 5, and `OpenVTC` holds 3 approved labs
   (`OpenVTC`, `DTG Credentials`, `Verifiable Trust Infrastructure`). Because a lab is scored on
   its most recent activity across *all* its repositories, one active sibling keeps the whole
   group out of `evaluate.md` and `at-risk.md`. Splitting them would raise repos.json from 55 to
   roughly 69 entries and match the site one-for-one.
3. **Two stale `labs/approved` pages** — `harmonia.md` and `fabric-token-sdk.md` — describe work
   that is archived or has graduated to project status. Worth raising with the labs site
   maintainers.
4. **`credebl`** names LFDT in its org description ("…Platform by Linux Foundation Decentralized
   Trust") but has no page under `labs/approved` and no proposal issue. Status unclear.
5. **`LFDT-Lineth`** blocks classic personal access tokens (`403 forbids access via a personal
   access token (classic)`). Read unauthenticated, its description is *"Lineth, an LF
   Decentralized Trust project."* — a project, not a lab, so out of scope, but any tooling that
   enumerates orgs with a classic PAT will error on it.

## Counts

| Classification by org description | Orgs |
| :--- | ---: |
| `…, an LF Decentralized Trust lab.` | 22 |
| `…, an LF Decentralized Trust project.` | 17 |
| Neither (umbrella, chapter, archive, ecosystem and unset orgs) | 19 |
| **Total orgs in `lf-decentralized-trust.yaml`** | **58** |

The org trailer alone is not a sufficient discovery rule: it misses `LFDT-tegaris` (no
description set) and every lab hosted inside the `hyperledger-labs`,
`LF-Decentralized-Trust-labs` and `hyperledger` umbrella orgs, which carry no per-lab
description. The `lab-proposals` issue tracker plus `labs/approved` is the reliable source.
