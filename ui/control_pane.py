"""Right pane – control buttons and log window."""

from __future__ import annotations

from datetime import datetime

import customtkinter as ctk


class ControlPane(ctk.CTkFrame):
    """Portal sync buttons and a scrollable log window.

    The buttons are placeholders for Phase 2 (Selenium automation).
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._build_widgets()

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)

        pad = {"padx": 12, "sticky": "ew"}

        row = 0

        # -- Header -------------------------------------------------------
        ctk.CTkLabel(
            self,
            text="Controls",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=row, column=0, padx=12, pady=(12, 8), sticky="w")
        row += 1

        # -- Buttons -------------------------------------------------------
        self._browser_btn = ctk.CTkButton(
            self, text="🌐  Launch Browser",
            command=lambda: self.log("Launch Browser clicked (Selenium not yet wired)."),
            fg_color="#2980b9", hover_color="#1f6fa5",
        )
        self._browser_btn.grid(row=row, column=0, pady=(4, 4), **pad)
        row += 1

        self._sync_pa_btn = ctk.CTkButton(
            self, text="⬆  Sync to PA",
            command=lambda: self.log("Sync to PA clicked (Selenium not yet wired)."),
            fg_color="#8e44ad", hover_color="#6c3483",
        )
        self._sync_pa_btn.grid(row=row, column=0, pady=4, **pad)
        row += 1

        self._sync_ea_btn = ctk.CTkButton(
            self, text="⬆  Sync to EA",
            command=lambda: self.log("Sync to EA clicked (Selenium not yet wired)."),
            fg_color="#d35400", hover_color="#a04000",
        )
        self._sync_ea_btn.grid(row=row, column=0, pady=4, **pad)
        row += 1

        # -- Separator -----------------------------------------------------
        ctk.CTkLabel(
            self,
            text="Activity Log",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=row, column=0, padx=12, pady=(16, 4), sticky="w")
        row += 1

        # -- Log window ----------------------------------------------------
        self._log_box = ctk.CTkTextbox(
            self,
            state="disabled",
            font=ctk.CTkFont(family="Courier", size=11),
            wrap="word",
        )
        self._log_box.grid(row=row, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.rowconfigure(row, weight=1)

        self.log("AutoCPD ready.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(self, message: str):
        """Append a timestamped message to the log window."""
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_box.configure(state="normal")
        self._log_box.insert("end", f"[{ts}]  {message}\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")
