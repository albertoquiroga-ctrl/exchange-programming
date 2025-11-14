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
        ALERTS["Change detector + console messenger"]
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
```

## Data flow notes
- Collectors run inside the CLI loop (or scheduler) using the configuration context.
- Each run persists the latest snapshot and reuses SQLite both for persistence and change detection.
- Alerts feed the CLI highlights and console transcript so presenters can narrate incidents directly from the terminal.

## Deployment view
- Local execution: `python -m hk_monitor.app` with mock data.
- Production: run collectors via cron/systemd and rely on the CLI for on-demand tiles and alert transcripts.
