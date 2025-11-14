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

## Typical workflows

* **Collect data once and show the CLI tiles**

  ```bash
  python -m hk_monitor.app --config config.toml --collect
  ```

* **Trigger alerts after running the collector**

  ```bash
  python -m hk_monitor.app --config config.toml --collect --alerts
  ```

* **Run the automated tests**

  ```bash
  pytest
  ```

The project defaults to the bundled mock JSON payloads so everything works offline.
