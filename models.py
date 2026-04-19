"""Data models and category constants for AutoCPD."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional


# ---------------------------------------------------------------------------
# Constants — the UI reads these dynamically.
# ---------------------------------------------------------------------------

DISCIPLINES: list[str] = [
    "Aerospace",
    "Biomedical",
    "Chemical",
    "Civil",
    "Electrical",
    "Environmental",
    "Geotechnical",
    "ITEE",
    "Mechanical",
    "Mechatronics",
    "Mining",
    "Software",
    "Structural",
]

UNIFIED_CATEGORIES: list[str] = [
    "Tertiary Education",
    "Short Courses / Workshops",
    "Workplace Learning",
    "Private Study",
    "Service to the Profession",
    "Preparation & Presentation",
    "Industry Involvement",
]


# ---------------------------------------------------------------------------
# Activity data-class
# ---------------------------------------------------------------------------

@dataclass
class Activity:
    """A single CPD diary entry.

    Each entry is mapped to both EA and PA portals using a unified discipline
    and category selection.
    """

    title: str
    date: str                              # ISO YYYY-MM-DD
    hours: float
    discipline: str
    category: str
    notes: str                             # free-text summary (up to ~1000 words)
    evidence_path: str
    provider_name: str = ""                # Optional: e.g. "Engineers Australia"
    provider_contact: str = ""             # Optional: e.g. "training@ea.org.au"
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

        Migrates legacy records transparently.
        """
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        
        # --- migrate old single-category / discipline records ----------
        if "category" not in data:
            if "ea_category" in data:
                data["category"] = data["ea_category"]
            elif "pa_category" in data:
                data["category"] = data["pa_category"]
            else:
                data["category"] = UNIFIED_CATEGORIES[0]

        if "discipline" not in data:
            data["discipline"] = DISCIPLINES[3]  # Default to Civil

        filtered = {k: v for k, v in data.items() if k in known_fields}

        # --- ensure basic defaults for status/notes if they were missing ---
        if "ea_status" not in filtered:
            filtered["ea_status"] = data.get("status", "Pending")
        if "pa_status" not in filtered:
            filtered["pa_status"] = "Pending"
        if "notes" not in filtered:
            filtered["notes"] = ""
        if "provider_name" not in filtered:
            filtered["provider_name"] = ""
        if "provider_contact" not in filtered:
            filtered["provider_contact"] = ""

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
