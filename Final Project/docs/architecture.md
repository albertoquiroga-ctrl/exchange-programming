# HK Conditions Monitor – Architecture

```mermaid
graph TD
    subgraph Inputs
        HKO_WARN["HKO Warning API"]
        HKO_RAIN["HKO Rainfall API"]
        HKO_AQHI["AQHI API"]
        TD_TRAFFIC["Transport Dept Traffic API"]
    end

    subgraph hk_monitor
        CFG["Config loader & validation"]
        COLLECT["Collector module"]
        DB[("SQLite snapshots")]
        ALERTS["Change detector + Telegram client"]
        CLI["Interactive CLI dashboard"]
    end

    HKO_WARN --> COLLECT
    HKO_RAIN --> COLLECT
    HKO_AQHI --> COLLECT
    TD_TRAFFIC --> COLLECT

    CFG --> COLLECT
    COLLECT --> DB
    DB --> CLI
    DB --> ALERTS
    ALERTS --> CLI
    ALERTS --> TELEGRAM["Telegram Bot API"]
```

## Data flow notes
- Collectors run inside the CLI loop (or scheduler) using the configuration context.
- Each run persists the latest snapshot and reuses SQLite both for persistence and change detection.
- Alerts feed both Telegram (live) and the CLI highlights so presenters can narrate incidents.

## Deployment view
- Local execution: `python -m hk_monitor.app` with mock data.
- Production: run collectors via cron/systemd and forward alerts to Telegram while the CLI offers on-demand tiles.
