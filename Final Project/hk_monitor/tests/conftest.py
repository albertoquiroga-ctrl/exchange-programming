from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT.parent) not in sys.path:
    # Ensure ``pytest`` can import hk_monitor even when running from the repo root.
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
