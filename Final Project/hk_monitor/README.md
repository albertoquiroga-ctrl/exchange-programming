# HK Conditions Monitor

This folder contains the reference implementation described in `Final Project/project-plan.md`.  It can run entirely on mock data for demos or switch to the real Hong Kong open-data APIs by setting `use_mock_data = false` in `config.toml`.

## Getting started

```bash
cd hk_monitor
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.template.toml config.toml
```

Adjust the config to point to your preferred district/station and optionally set the Telegram bot token/chat ID.

## Interactive console dashboard

The CLI now launches an interactive dashboard.  After selecting your configuration file you can:

* Press **Enter** to refresh the four tiles immediately.
* Type **d**, **a** or **t** to switch the monitored rain district, AQHI station or traffic region using the values discovered in the bundled mock payloads.
* Pass `--alerts` to enable Telegram change detection — tiles that triggered an alert on the last refresh are highlighted inline.
* Review the **pandas-powered AQHI history table** that now appears under every snapshot, summarising the most recent readings, their mean/min/max and the latest change.  It makes the console demo feel closer to a mini dashboard than a set of raw HTTP calls.

Example command:

```bash
python -m hk_monitor.app --config config.toml --alerts
```

Each refresh honours `app.poll_interval` (default 300 s) before collecting the next snapshot; adjust it in `config.toml` for faster demos.

Use `--collect` the first time you run the dashboard to pull an initial snapshot before entering the menu.

To showcase the pandas integration in isolation, run the dedicated test:

```bash
pytest tests/test_history_summary.py -k history
```
This exercises the helper that builds the AQHI table so you can paste the output directly into demo slides.

## Testing and scenario scripts

Run the whole suite (including the three scripted scenarios requested in the project plan) with:

```bash
pytest
```

* `tests/test_scenarios.py` implements the “warning upgrade”, “AQHI spike” and “traffic incident” narratives, driving the collector with dedicated mock payloads and verifying that `ChangeDetector` emits alerts for each case.
* `tests/test_config.py` enforces the stricter configuration validation so mistakes are caught before running the collectors.

The project defaults to the bundled mock JSON payloads so everything works offline.
