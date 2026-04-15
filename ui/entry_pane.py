"""Left pane – CPD activity entry / edit form."""

from __future__ import annotations

import os
from datetime import date
from tkinter import filedialog, StringVar

import customtkinter as ctk

from models import Activity, CATEGORY_MAP, PORTALS


class EntryPane(ctk.CTkFrame):
    """Input form for creating and editing CPD diary entries.

    When a row is selected in the diary table the form is populated with that
    record's data and the primary button switches to **Update**.  Clicking
    *Clear* resets back to *Add* mode.
    """

    def __init__(self, master, on_save_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_save = on_save_callback  # called after add / update
        self._editing_id: str | None = None  # set when editing an existing record

        self._build_widgets()

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)

        pad = {"padx": 12, "pady": (4, 0), "sticky": "w"}
        entry_pad = {"padx": 12, "pady": (0, 6), "sticky": "ew"}

        row = 0

        # -- Header -------------------------------------------------------
        header = ctk.CTkLabel(self, text="CPD Entry", font=ctk.CTkFont(size=18, weight="bold"))
        header.grid(row=row, column=0, padx=12, pady=(12, 8), sticky="w")
        row += 1

        # -- Portal selector (EA / PA) ------------------------------------
        ctk.CTkLabel(self, text="Portal").grid(row=row, column=0, **pad)
        row += 1
        self._portal_var = StringVar(value=PORTALS[0])
        self._portal_menu = ctk.CTkOptionMenu(
            self,
            variable=self._portal_var,
            values=PORTALS,
            command=self._on_portal_changed,
        )
        self._portal_menu.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- Title ---------------------------------------------------------
        ctk.CTkLabel(self, text="Title *").grid(row=row, column=0, **pad)
        row += 1
        self._title_entry = ctk.CTkEntry(self, placeholder_text="e.g. Bridge Design Seminar")
        self._title_entry.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- Date ----------------------------------------------------------
        ctk.CTkLabel(self, text="Date (YYYY-MM-DD) *").grid(row=row, column=0, **pad)
        row += 1
        self._date_entry = ctk.CTkEntry(self, placeholder_text=date.today().isoformat())
        self._date_entry.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- Hours ---------------------------------------------------------
        ctk.CTkLabel(self, text="Hours *").grid(row=row, column=0, **pad)
        row += 1
        self._hours_entry = ctk.CTkEntry(self, placeholder_text="e.g. 1.5")
        self._hours_entry.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- Category ------------------------------------------------------
        ctk.CTkLabel(self, text="Category *").grid(row=row, column=0, **pad)
        row += 1
        self._category_var = StringVar(value="")
        self._category_menu = ctk.CTkOptionMenu(
            self,
            variable=self._category_var,
            values=CATEGORY_MAP[self._portal_var.get()],
        )
        self._category_menu.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- Evidence file path --------------------------------------------
        ctk.CTkLabel(self, text="Evidence File *").grid(row=row, column=0, **pad)
        row += 1

        evidence_frame = ctk.CTkFrame(self, fg_color="transparent")
        evidence_frame.grid(row=row, column=0, **entry_pad)
        evidence_frame.columnconfigure(0, weight=1)

        self._evidence_entry = ctk.CTkEntry(
            evidence_frame,
            placeholder_text="Drag & drop or browse…",
        )
        self._evidence_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        browse_btn = ctk.CTkButton(
            evidence_frame, text="Browse", width=70,
            command=self._browse_evidence,
        )
        browse_btn.grid(row=0, column=1)
        row += 1

        # -- Drop target overlay (visual cue) -----------------------------
        self._drop_label = ctk.CTkLabel(
            self,
            text="↓  Drop evidence file here  ↓",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        )
        self._drop_label.grid(row=row, column=0, padx=12, pady=(0, 4))
        row += 1

        # -- Action buttons ------------------------------------------------
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=row, column=0, padx=12, pady=(8, 12), sticky="ew")
        btn_frame.columnconfigure((0, 1), weight=1)

        self._action_btn = ctk.CTkButton(
            btn_frame,
            text="Add Entry",
            command=self._on_action,
            fg_color="#2fa572",
            hover_color="#26855c",
        )
        self._action_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self._clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            command=self.clear_form,
            fg_color="gray40",
            hover_color="gray30",
        )
        self._clear_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        row += 1

        # -- Validation feedback -------------------------------------------
        self._error_label = ctk.CTkLabel(self, text="", text_color="#e05050", font=ctk.CTkFont(size=11))
        self._error_label.grid(row=row, column=0, padx=12, sticky="w")

        # -- Enable drag-and-drop if tkdnd is available --------------------
        self._setup_dnd()

    # ------------------------------------------------------------------
    # Drag-and-drop support
    # ------------------------------------------------------------------

    def _setup_dnd(self):
        """Register the evidence entry as a file drop target using tkdnd."""
        try:
            self._evidence_entry.drop_target_register("DND_Files")  # type: ignore[attr-defined]
            self._evidence_entry.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
        except (AttributeError, Exception):
            # tkdnd / tkinterdnd2 not available — silently fall back to browse-only
            pass

    def _on_drop(self, event):
        """Handle a file drop onto the evidence entry."""
        path = event.data.strip().strip("{}")  # tkdnd wraps paths in braces on some platforms
        self._evidence_entry.delete(0, "end")
        self._evidence_entry.insert(0, path)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_portal_changed(self, portal: str):
        """Refresh the category dropdown when the portal changes."""
        cats = CATEGORY_MAP.get(portal, [])
        self._category_menu.configure(values=cats)
        if cats:
            self._category_var.set(cats[0])

    def _browse_evidence(self):
        path = filedialog.askopenfilename(
            title="Select evidence file",
            filetypes=[("All files", "*.*"), ("PDF", "*.pdf"), ("Images", "*.png *.jpg *.jpeg")],
        )
        if path:
            self._evidence_entry.delete(0, "end")
            self._evidence_entry.insert(0, path)

    def _on_action(self):
        """Validate and either add a new entry or update the selected one."""
        title = self._title_entry.get().strip()
        date_str = self._date_entry.get().strip()
        hours_str = self._hours_entry.get().strip()
        category = self._category_var.get()
        evidence = self._evidence_entry.get().strip()

        # --- validation ---------------------------------------------------
        errors: list[str] = []
        if not title:
            errors.append("Title is required.")
        if not Activity.validate_date(date_str):
            errors.append("Date must be YYYY-MM-DD.")
        if not Activity.validate_hours(hours_str):
            errors.append("Hours must be a positive number.")
        if not category:
            errors.append("Select a category.")
        if not evidence:
            errors.append("Evidence file is required.")
        if errors:
            self._error_label.configure(text="  •  ".join(errors))
            return
        self._error_label.configure(text="")

        hours = float(hours_str)

        if self._editing_id:
            # Update existing record
            from storage import update_activity
            update_activity(
                self._editing_id,
                title=title,
                date=date_str,
                hours=hours,
                category=category,
                evidence_path=evidence,
            )
        else:
            # Add new record
            from storage import add_activity
            activity = Activity(
                title=title,
                date=date_str,
                hours=hours,
                category=category,
                evidence_path=evidence,
            )
            add_activity(activity)

        self.clear_form()
        if self._on_save:
            self._on_save()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def populate(self, activity: Activity):
        """Fill the form with an existing activity for editing."""
        self._editing_id = activity.id
        self._action_btn.configure(text="Update Entry", fg_color="#2980b9", hover_color="#1f6fa5")

        self._title_entry.delete(0, "end")
        self._title_entry.insert(0, activity.title)

        self._date_entry.delete(0, "end")
        self._date_entry.insert(0, activity.date)

        self._hours_entry.delete(0, "end")
        self._hours_entry.insert(0, str(activity.hours))

        self._evidence_entry.delete(0, "end")
        self._evidence_entry.insert(0, activity.evidence_path)

        # Set portal + category (detect which portal the category belongs to)
        for portal, cats in CATEGORY_MAP.items():
            if activity.category in cats:
                self._portal_var.set(portal)
                self._on_portal_changed(portal)
                break
        self._category_var.set(activity.category)

    def clear_form(self):
        """Reset all fields and return to Add mode."""
        self._editing_id = None
        self._action_btn.configure(text="Add Entry", fg_color="#2fa572", hover_color="#26855c")
        self._error_label.configure(text="")

        self._title_entry.delete(0, "end")
        self._date_entry.delete(0, "end")
        self._hours_entry.delete(0, "end")
        self._evidence_entry.delete(0, "end")
        self._category_var.set(CATEGORY_MAP[self._portal_var.get()][0])
