"""Main application window for AutoCPD — one-screen, three-pane dashboard."""

from __future__ import annotations

import customtkinter as ctk

from ui.entry_pane import EntryPane
from ui.diary_pane import DiaryPane
from ui.control_pane import ControlPane


class AutoCPDApp(ctk.CTk):
    """Top-level CustomTkinter window.

    Layout
    ------
    ┌────────────┬──────────────────┬────────────┐
    │  EntryPane │    DiaryPane     │ ControlPane│
    │  (col 0)   │     (col 1)      │  (col 2)   │
    └────────────┴──────────────────┴────────────┘
    """

    def __init__(self):
        # Theme MUST be set before CTk() is instantiated
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        super().__init__()

        # -- Window settings ------------------------------------------------
        self.title("AutoCPD — CPD Diary")
        self.geometry("1200x680")
        self.minsize(900, 500)

        # -- Grid layout (3 columns) ----------------------------------------
        self.columnconfigure(0, weight=3)   # entry pane
        self.columnconfigure(1, weight=5)   # diary (wider)
        self.columnconfigure(2, weight=3)   # controls
        self.rowconfigure(0, weight=1)

        # -- Panes ----------------------------------------------------------
        self.diary_pane = DiaryPane(
            self,
            on_select_callback=self._on_diary_select,
            corner_radius=8,
        )
        self.diary_pane.grid(row=0, column=1, sticky="nsew", padx=6, pady=8)

        self.entry_pane = EntryPane(
            self,
            on_save_callback=self._on_entry_saved,
            on_delete_callback=self._on_entry_deleted,
            corner_radius=8,
        )
        self.entry_pane.grid(row=0, column=0, sticky="nsew", padx=(8, 6), pady=8)

        self.control_pane = ControlPane(
            self,
            corner_radius=8,
        )
        self.control_pane.grid(row=0, column=2, sticky="nsew", padx=(6, 8), pady=8)

    # ------------------------------------------------------------------
    # Inter-pane communication
    # ------------------------------------------------------------------

    def _on_entry_saved(self):
        """Called after an entry is added or updated."""
        self.diary_pane.refresh()
        self.control_pane.log("Entry saved ✓")

    def _on_entry_deleted(self):
        """Called after an entry is deleted from the entry pane."""
        self.diary_pane.refresh()
        self.control_pane.log("Entry deleted 🗑")

    def _on_diary_select(self, activity):
        """Called when the user clicks a row in the diary table."""
        self.entry_pane.populate(activity)
