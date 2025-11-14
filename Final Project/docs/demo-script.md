# Demo Script

1. **Prep**
   - Ensure `config.toml` points to mock data and `telegram.test_mode = true`.
   - Run `pytest` to show all narrative scripts passing.

2. **CLI walkthrough**
   - Command: `python -m hk_monitor.app --config config.toml --collect --alerts`.
   - Narrate how the menu appears and explain the available shortcuts.
   - Change the rain district and AQHI station live to showcase configurability.

3. **Warning upgrade scenario**
   - Swap `mocks.warnings` in `config.toml` to `tests/data/warnings_red.json` and refresh.
   - Point out the highlighted **Warnings** tile and the Telegram dry-run output.

4. **AQHI spike scenario**
   - Use `tests/data/aqhi_spike.json` as the AQHI mock payload.
   - Refresh twice; on the second refresh the AQHI tile is highlighted.

5. **Traffic incident scenario**
   - Switch `mocks.traffic` to `tests/data/traffic_incident.json`.
   - Refresh until the severity escalates; narrate the alert message and describe the recommended commuter action.

6. **Wrap-up**
   - Summarise architecture (reference the diagram), validation, tests, and next steps.
