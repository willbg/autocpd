"""Data models and category constants for AutoCPD."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional


# ---------------------------------------------------------------------------
# Category lists — append freely; the UI reads these dynamically.
# ---------------------------------------------------------------------------

EA_CATEGORIES: list[str] = [
    "Type I – Tertiary Education",
    "Type II – Short Courses / Workshops",
    "Type III – Learning on the Job",
]

PA_CATEGORIES: list[str] = [
    "Technical",
    "Management",
    "Soft Skills",
]


# ---------------------------------------------------------------------------
# Activity data-class
# ---------------------------------------------------------------------------

@dataclass
class Activity:
    """A single CPD diary entry.

    Each entry is mapped to *both* EA and PA portals with independent
    category selections and upload statuses.
    """

    title: str
    date: str                              # ISO YYYY-MM-DD
    hours: float
    ea_category: str
    pa_category: str
    notes: str                             # free-text summary (up to ~1000 words)
    evidence_path: str
    ea_status: str = "Pending"             # "Pending" | "Uploaded"
    pa_status: str = "Pending"             # "Pending" | "Uploaded"
    selected: bool = False                 # checkbox for bulk upload
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # -- serialisation helpers ------------------------------------------------

    def to_dict(self) -> dict:
        """Return a plain dict suitable for JSON serialisation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Activity:
        """Construct an Activity from a dict (e.g. loaded from JSON).

        Migrates legacy single-field records transparently.
        """
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}

        # --- migrate old single-category / single-status records ----------
        if "category" in data and "ea_category" not in filtered:
            filtered["ea_category"] = data["category"]
        if "category" in data and "pa_category" not in filtered:
            filtered["pa_category"] = ""
        if "status" in data and "ea_status" not in filtered:
            filtered["ea_status"] = data["status"]
        if "status" in data and "pa_status" not in filtered:
            filtered["pa_status"] = "Pending"
        if "notes" not in filtered:
            filtered["notes"] = ""

        return cls(**filtered)

    # -- convenience ----------------------------------------------------------

    @staticmethod
    def validate_date(value: str) -> bool:
        """Return True if *value* is a valid YYYY-MM-DD string."""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_hours(value: str) -> bool:
        """Return True if *value* is a positive float."""
        try:
            return float(value) > 0
        except ValueError:
            return False
