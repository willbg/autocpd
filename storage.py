"""JSON-based persistence for CPD diary activities.

Data is stored in ``activities.json`` next to the running script (or inside
the PyInstaller temp directory when running as a bundled executable).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

from models import Activity


# ---------------------------------------------------------------------------
# Path resolution (PyInstaller-aware)
# ---------------------------------------------------------------------------

def _data_dir() -> Path:
    """Return the directory used for persistent data files.

    When running from a PyInstaller bundle the writable data directory is
    the folder that contains the .exe (not ``sys._MEIPASS`` which is a
    read-only temp folder).  During development it's simply the repo root.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller one-file: use the directory the exe lives in
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


ACTIVITIES_FILE = _data_dir() / "activities.json"


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def load_activities() -> list[Activity]:
    """Read all activities from disk.  Returns [] if the file is missing."""
    if not ACTIVITIES_FILE.exists():
        return []
    with open(ACTIVITIES_FILE, "r", encoding="utf-8") as fh:
        raw: list[dict] = json.load(fh)
    return [Activity.from_dict(d) for d in raw]


def save_activities(activities: list[Activity]) -> None:
    """Overwrite the JSON file with the given list of activities."""
    with open(ACTIVITIES_FILE, "w", encoding="utf-8") as fh:
        json.dump([a.to_dict() for a in activities], fh, indent=2)


def add_activity(activity: Activity) -> None:
    """Append a single activity and persist."""
    activities = load_activities()
    activities.append(activity)
    save_activities(activities)


def update_activity(activity_id: str, **fields) -> Optional[Activity]:
    """Update fields on the activity with *activity_id*. Returns the updated
    activity, or ``None`` if not found."""
    activities = load_activities()
    for act in activities:
        if act.id == activity_id:
            for key, value in fields.items():
                if hasattr(act, key):
                    setattr(act, key, value)
            save_activities(activities)
            return act
    return None


def delete_activity(activity_id: str) -> bool:
    """Remove the activity with *activity_id*. Returns True if found."""
    activities = load_activities()
    before = len(activities)
    activities = [a for a in activities if a.id != activity_id]
    if len(activities) < before:
        save_activities(activities)
        return True
    return False
