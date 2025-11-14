# HK Conditions Monitor – Owner Map

| Role | Teammate | Focus | Key Deliverables |
| --- | --- | --- | --- |
| Dev A – Tech Lead / Integrator | Ada Liu | Repo scaffolding, integration, logging | Project skeleton, CI instructions, integration fixes |
| Dev B – API & Collector Lead | Marcus Ng | Endpoint research, fetchers, mocks | API docs, mock payloads, working collectors |
| Dev C – DB & Modeling | Priya Desai | Schema design, `db.py` implementation | Schema doc, migration/init script, CRUD helpers |
| Dev D – Alerts & Telegram | Calvin Ho | Change detection, alert delivery | Severity mapping, alert engine, Telegram client |
| Dev E – CLI & Testing | Renee Zhang | User-facing CLI, unit tests, demo scripts | `app.py`, pytest suite, scenario scripts |
| Dev F – PM / Docs | Gabriel Fung | Coordination, slides/report, presentation prep | Meeting notes, diagrams, slide deck, demo choreography |

## Peer-review deliverable summaries
- **Ada Liu (Dev A):** established the repo scaffolding, added logging defaults, and drove the final integration polish before the live demo.
- **Marcus Ng (Dev B):** documented each API, curated mock payloads, and delivered the production-ready collectors with retry logic.
- **Priya Desai (Dev C):** modeled the SQLite schema, shipped the `db.py` helpers, and maintained the initialization/migration scripts.
- **Calvin Ho (Dev D):** implemented the change-detection flow, tuned severity mappings, and wrapped Telegram delivery plus console fallbacks.
- **Renee Zhang (Dev E):** built the interactive CLI, wired the alert highlights, and wrote the pytest scenarios requested in the plan.
- **Gabriel Fung (Dev F):** coordinated timelines, created diagrams and slides, and rehearsed the end-to-end demo choreography.
