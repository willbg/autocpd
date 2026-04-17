"""Main application window for AutoCPD — one-screen, two-column dashboard."""

from __future__ import annotations

import customtkinter as ctk

from ui.entry_pane import EntryPane
from ui.diary_pane import DiaryPane
from ui.control_pane import LogPane


class AutoCPDApp(ctk.CTk):
    """Top-level CustomTkinter window.

    Layout
    ------
    ┌──────────────────┬──────────────────────────┐
    │                  │                           │
    │   EntryPane      │       DiaryPane           │
    │                  │      (row 0, ~80%)        │
    │                  ├───────────────────────────┤
    │                  │                           │
    │  ─ ─ ─ ─ ─ ─ ─  │     Activity Log          │
    │  Control Buttons │      (row 1, ~20%)        │
    │                  │                           │
    └──────────────────┴───────────────────────────┘
       col 0                    col 1
    """

    def __init__(self):
        # Theme MUST be set before CTk() is instantiated
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        super().__init__()

        # -- Window settings ------------------------------------------------
        self.title("AutoCPD — CPD Diary")
        self.geometry("1300x850")
        self.minsize(1000, 600)

        # -- Grid layout (2 columns, 2 rows) --------------------------------
        self.columnconfigure(0, weight=3)   # left: entry + controls
        self.columnconfigure(1, weight=5)   # right: diary + log
        self.rowconfigure(0, weight=4)      # ~80% diary
        self.rowconfigure(1, weight=1)      # ~20% log

        # -- Left column (spans both rows) ----------------------------------
        self.entry_pane = EntryPane(
            self,
            on_save_callback=self._on_entry_saved,
            on_delete_callback=self._on_entry_deleted,
            log_callback=self._log,
            corner_radius=8,
        )
        self.entry_pane.grid(
            row=0, column=0, rowspan=2,
            sticky="nsew", padx=(8, 6), pady=8,
        )

        # -- Right column, top row: diary -----------------------------------
        self.diary_pane = DiaryPane(
            self,
            on_select_callback=self._on_diary_select,
            corner_radius=8,
        )
        self.diary_pane.grid(
            row=0, column=1,
            sticky="nsew", padx=(6, 8), pady=(8, 4),
        )

        # -- Right column, bottom row: activity log -------------------------
        self.log_pane = LogPane(
            self,
            corner_radius=8,
        )
        self.log_pane.grid(
            row=1, column=1,
            sticky="nsew", padx=(6, 8), pady=(4, 8),
        )

        # -- Force foreground on launch (macOS workaround) -----------------
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))
        self.focus_force()

    # ------------------------------------------------------------------
    # Inter-pane communication
    # ------------------------------------------------------------------

    def _log(self, message: str):
        """Write a message to the activity log pane."""
        self.log_pane.log(message)

    def _on_entry_saved(self):
        """Called after an entry is added or updated."""
        self.diary_pane.refresh()
        self.log_pane.log("Entry saved ✓")

    def _on_entry_deleted(self):
        """Called after an entry is deleted from the entry pane."""
        self.diary_pane.refresh()
        self.log_pane.log("Entry deleted 🗑")

    def _on_diary_select(self, activity):
        """Called when the user clicks a row in the diary table."""
        self.entry_pane.populate(activity)
