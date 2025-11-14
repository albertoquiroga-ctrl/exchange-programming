# HK Conditions Monitor – Presentation Outline

## 1. Problem framing
- Hong Kong residents juggle multiple feeds (HKO warnings, AQHI, rainfall, TD traffic) to decide on commutes.
- Alerts arrive through different channels and lack persistence/history.
- Goal: unify the feeds into a single dashboard plus proactive console alerts.

## 2. Solution overview
- Python console dashboard backed by SQLite snapshots.
- Scheduled collectors fetch warnings, rainfall, AQHI and traffic every few minutes.
- Change detector logs alerts to the console and highlights tiles when categories escalate.
- Mock payloads allow offline demos and reproducible tests.

## 3. Architecture slide
- Show component diagram (see `architecture.md`).
- Highlight config-driven collectors, storage layer, alert router and CLI interface.

## 4. Demo flow
- Start CLI, load config, pick district/station/region via interactive menu.
- Trigger refreshes, show highlighted tiles when alerts fire.
- Run scripted scenarios (warning upgrade, AQHI spike, traffic incident) and narrate the console alert transcript.

## 5. Results & metrics
- Latency: <5s per refresh when using mock data.
- Coverage: four official data sources plus local alert/highlight integration.
- Reliability: deterministic tests for collectors, config validation and scenarios.

## 6. Lessons learned
- Importance of validating configuration early.
- Designing tests around real-world narratives keeps demos focused.
- Mock-first approach speeds up development when APIs throttle.

## 7. Next steps
- Add web UI or SMS integration.
- Extend database retention for time-series analysis.
- Automate deployment (cron job or serverless collector).
