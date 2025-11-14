# HK Conditions Monitor – Owner Map

| Role | Teammate | Readability stream | Updated ownership focus |
| --- | --- | --- | --- |
| Dev A – Tech Lead / Integrator | Ada Liu | Redistribution narrative | Curate the repo-root `README.md`, hk_monitor README, and config templates so the redistribution story and onboarding links stay in sync. |
| Dev B – API & Collector Lead | Marcus Ng | Legible rewrite | Refactor all collectors plus `config.py` entry points until the dataflow reads like a narrated walkthrough with docstrings and helper functions. |
| Dev C – DB & Modeling | Priya Desai | Legible rewrite | Apply the same tutorial-style cleanup to `db.py`, schema diagrams, and the state-machine notes that explain how collectors persist snapshots. |
| Dev D – Alerts & Console | Calvin Ho | Heavy commenting & onboarding aids | Layer inline explanations across `alerts.py` and console glue code, plus record the alert escalation SOP referenced by the onboarding doc. |
| Dev E – CLI & Testing | Renee Zhang | Heavy commenting & onboarding aids | Document the CLI/test interfaces, annotate pytest fixtures, and maintain the “day-one runbook” linking test commands to expected output. |
| Dev F – PM / Docs | Gabriel Fung | Redistribution narrative | Thread the redistribution context into slides, diagrams, and doc issue templates so cross-team reviewers land on the same story. |

## Day-to-day shifts under the readability push
- **Ada Liu (Dev A):** splits her time between reviewing pull requests and ensuring every repo-touching doc points to the new readability plan; she now runs a daily link check to confirm config tables, owner map, and README anchors stay aligned.
- **Marcus Ng (Dev B):** dedicates each workday to one collector module, rewriting long functions into smaller helpers, adding docstrings/tests, and pairing with Priya to keep terminology identical between fetchers and persistence.
- **Priya Desai (Dev C):** focuses on demystifying `db.py`: she keeps an architecture sketch open during development, renames tables/fields for clarity, and narrates schema changes directly inside migration comments before handing them to Marcus.
- **Calvin Ho (Dev D):** treats alerts as the onboarding classroom; he records inline commentary for every severity transition, authors SOP snippets that explain when humans intervene, and syncs them with Renee’s CLI notes.
- **Renee Zhang (Dev E):** maintains the CLI walkthrough and pytest runbook; her daily routine now includes expanding fixture comments, embedding terminal transcripts, and verifying that newcomers can replay the tests without guessing flags.
- **Gabriel Fung (Dev F):** stewards the narrative glue—he audits slides, doc templates, and meeting notes so they mirror the redistribution milestones and hosts twice-weekly check-ins to capture any onboarding blockers uncovered by the team.
