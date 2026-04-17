"""Activity log pane — scrollable timestamped message log."""

from __future__ import annotations

from datetime import datetime

import customtkinter as ctk


class LogPane(ctk.CTkFrame):
    """Read-only scrollable log window showing timestamped status messages."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._build_widgets()

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Activity Log",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=12, pady=(8, 4), sticky="w")

        self._log_box = ctk.CTkTextbox(
            self,
            state="disabled",
            font=ctk.CTkFont(family="Courier", size=11),
            wrap="word",
        )
        self._log_box.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="nsew")

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
