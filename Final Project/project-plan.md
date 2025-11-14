# HK Conditions Monitor – Project Plan

This plan turns the initial concept (console-first monitoring toolkit for HKO/EPD/TD data) into a concrete roadmap for a 6-person team over ~3 weeks.

## 1. Assumptions & Scope
- **Language:** Python 3.10+.
- **Runtime:** Console/CLI demo; no web UI.
- **APIs to showcase:**
  - Hong Kong Observatory (HKO) warnings summary.
  - HKO rainfall nowcast by district.
  - Environmental Protection Department (EPD) AQHI feed.
  - Transport Department disruption summaries.
- **Infra:** Local execution, SQLite for persistence, optional terminal alerts/highlights driven by the change detector.
- **Deliverables:** Running CLI demo, console alert transcript/highlights, architecture/dataflow diagrams, short report/slides.

## 2. Architecture Overview
```
config.toml/.env  →  config.py  →  shared settings & secrets
                       ↓
collector.py  →  db.py (SQLite)  →  tables: warnings, rain, aqhi, traffic
                      ↓
alerts.py  →  console notifications/highlights on state changes
                       ↓
app.py CLI  →  prints latest tiles, accepts simple user input
```
**Supporting modules:** `utils/logging.py`, `tests/` (unit tests + demo scripts), `tests/data/` (mock JSON payloads).

### Module responsibilities
| Module | Responsibilities |
| --- | --- |
| `config.py` | Load config, validate required keys (API endpoints, polling interval, district list). |
| `db.py` | Initialize SQLite schema, insert snapshots, fetch previous/current rows, expose query helpers per metric. |
| `collector.py` | Poll each API, normalize payloads into canonical dicts, persist into DB, handle network failures + caching fallback. |
| `alerts.py` | Compare consecutive snapshots, map values into severity buckets, send alerts to the console/highlight tiles, dedupe events. |
| `app.py` | CLI wrapper: choose district/station, show latest snapshot per tile, refresh view, print timestamps. |
| `tests/` | Unit tests for parsers & change detection plus demo scripts simulating notable scenarios. |

## 3. Work Packages
1. **Environment & Scaffolding**
   - Repo structure (`src/` or flat), `requirements.txt`, `.env`/`config.template.toml`, logging defaults.
2. **API Research & Mock Data**
   - Confirm endpoints, auth, rate limits; store 2–3 JSON samples per API inside `tests/data/`; document category mappings.
3. **Database Schema & Data Model**
   - Define tables (`warnings`, `rain`, `aqhi`, `traffic`) with timestamps + district/station columns; implement `db.py` helpers.
4. **Collector Implementation**
   - Functions: `fetch_warnings`, `fetch_rain`, `fetch_aqhi`, `fetch_traffic`; normalization; persistence; retry/fallback strategy.
5. **Alerts & Console Integration**
   - Change detection engine, severity mapping per metric, CLI messenger/highlight plumbing.
6. **CLI Demo (`app.py`)**
   - Render four tiles + last updated timestamps; allow district/station selection; refresh action; highlight active alerts.
7. **Testing & Demo Scripts**
   - Pytest/unit tests for parsers, category mapping, and change detection; scenario scripts: warning upgrade, AQHI spike, traffic incident.
8. **Slides/Report**
   - Architecture/dataflow diagrams, screenshots (CLI views + alert transcripts), summary of libraries, lessons learned.

## 4. Team Roles & Ownership
| Role | Focus | Key Deliverables |
| --- | --- | --- |
| **Dev A – Tech Lead / Integrator** | Repo scaffolding, integration, logging | Project skeleton, CI instructions, final integration fixes |
| **Dev B – API & Collector Lead** | Endpoint research, fetchers, mocks | API docs, mock payloads, working collectors |
| **Dev C – DB & Modeling** | Schema design, `db.py` implementation | Schema doc, migration/init script, CRUD helpers |
| **Dev D – Alerts & Console** | Change detection, alert delivery | Severity mapping, alert engine, console messenger/highlighting |
| **Dev E – CLI & Testing** | User-facing CLI, unit tests, demo scripts | `app.py`, pytest suite, scenario scripts |
| **Dev F – PM / Docs** | Coordination, slides/report, presentation prep | Meeting notes, diagrams, slide deck, demo choreography |

## 5. Timeline & Meetings (3-week window)
| Week | Meeting | Objectives |
| --- | --- | --- |
| Week 1, Day 0 | **Kickoff & Architecture (60–90 min)** | Confirm scope, assign roles, agree on tech stack & repo rules. |
| Week 1, Day 3–4 | **API & Schema Review (45–60 min)** | Freeze API mappings, DB schema, category values. |
| Week 2, Day 7–8 | **Mid-project Integration (60–90 min)** | Run collector → DB → CLI flow; identify integration bugs. |
| Week 2, Day 11–12 | **Feature Freeze & Test Plan (45–60 min)** | Declare feature freeze, prioritize bugfixes, lock demo scenarios. |
| Week 3, Day 14–15 | **Full Rehearsal (60–90 min)** | Dry-run slides + live demo + console alert walk-through; finalize presenters. |

## 6. Immediate Action Items
1. **Repo skeleton:** Dev A creates structure, `requirements.txt`, config templates, logging baseline.
2. **Role confirmation:** Map real team members to Dev A–F in `README` or `docs/owners.md`.
3. **Schedule meetings:** Put all five meetings on the calendar.
4. **Parallel kick-off:** Dev B starts API docs + mock payload collection; Dev C drafts schema + `db.py` stubs.
5. **Deliverable shell:** Dev F creates slide outline (Problem → Solution → Architecture → Demo → Lessons) so assets can drop in later.

## 7. Success Criteria
- CLI demo shows four tiles with recent data + timestamps.
- Alerts trigger only on state/category transitions and demonstrate via the console log/highlight summary.
- SQLite DB stores snapshots and allows quick retrieval of latest + previous states per metric.
- Mock datasets enable offline demos when APIs are unreachable.
- Presentation includes diagrams, screenshots, and a narrated demo path tested in rehearsal.
