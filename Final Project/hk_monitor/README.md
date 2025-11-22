# HK Conditions Monitor (beginner-friendly)

This project is a single Python file that shows live Hong Kong weather, air quality, and traffic data in the terminal. There are no config files or databases to set up.

## What the code does
- Fetches live data from public HK APIs (warnings, rain, AQHI, traffic).
- Prints the latest values in a simple text dashboard.
- Lets you switch locations (district/station/region) by picking a number from a menu.
- Keeps everything in memory; nothing is stored on disk.

## How to run
1) Open a terminal at `Final Project/hk_monitor`
2) Activate your virtual environment if you have one
3) Run:
   ```bash
   python app.py
   ```

## How to use the console
- Press **Enter** to refresh the data.
- Press **c** to change locations; type the number shown in the menu to pick a new district/station/region.
- Press **q** to quit.

## How the code is organized
- `app.py` is the only file. Key parts:
  - Default settings at the top (district, station, region, refresh interval).
  - URL constants for each HK API.
  - `_collect_snapshot` grabs warnings, rain, AQHI, and traffic.
  - `_print_snapshot` formats the dashboard.
  - `_change_locations` shows menus and updates the current selections.
  - Small helpers to parse timestamps and classify rain/AQHI levels.

Read through `app.py` from top to bottom—comments and function names describe each step. You can change the default district/station/region by editing the `DEFAULTS` dictionary near the top.***
